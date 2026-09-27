import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DatasetNotFoundException,
    PreprocessingRequiredException,
    ProfileRequiredException,
    VisualizationException,
    VisualizationNotFoundException,
)
from app.core.logging import logger
from app.db.models.dataset import Dataset
from app.db.models.visualization_run import VisualizationRun
from app.db.models.visualization_recommendation import VisualizationRecommendation
from app.db.repositories.dataset_repository import DatasetRepository
from app.db.repositories.profile_repository import ProfileRepository
from app.db.repositories.preprocessing_repository import PreprocessingRepository
from app.db.repositories.visualization_repository import VisualizationRepository
from app.services.dataset_loader import DatasetLoader
from app.services.chart_spec_builder import ChartSpecBuilder
from app.services.storage_service import StorageService
from app.services.visualization_planner import VisualizationPlanner
from app.services.visualization_scoring import VisualizationScoringEngine
from app.services.visualization_validator import VisualizationValidator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VisualizationService:
    """Service orchestrating visualization generation runs, recommendation scoring, and chart data extraction."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.profile_repo = ProfileRepository(session)
        self.prep_repo = PreprocessingRepository(session)
        self.viz_repo = VisualizationRepository(session)
        self.storage_service = StorageService()
        self.validator = VisualizationValidator()
        self.planner = VisualizationPlanner()
        self.scoring_engine = VisualizationScoringEngine()
        self.chart_builder = ChartSpecBuilder()

    async def get_processed_dataset(self, source_dataset: Dataset) -> Dataset:
        if source_dataset.dataset_kind == "PROCESSED":
            return source_dataset

        # Find derived processed dataset
        prep_job = await self.prep_repo.get_latest_job_for_dataset(source_dataset.id)
        if not prep_job or not prep_job.output_dataset_id or prep_job.status != "COMPLETED":
            raise PreprocessingRequiredException(
                f"Dataset '{source_dataset.id}' has not been preprocessed. Phase 4 preprocessing is required before generating visualizations."
            )

        processed_dataset = await self.dataset_repo.get_by_id(prep_job.output_dataset_id)
        if not processed_dataset:
            raise PreprocessingRequiredException("Processed dataset record not found.")

        return processed_dataset

    async def generate_visualizations(
        self, dataset_id: uuid.UUID
    ) -> Tuple[VisualizationRun, List[VisualizationRecommendation]]:
        source_dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not source_dataset:
            raise DatasetNotFoundException(f"Dataset with ID {dataset_id} not found.")

        processed_dataset = await self.get_processed_dataset(source_dataset)
        profile = await self.profile_repo.get_profile_by_dataset_id(dataset_id)
        if not profile:
            raise ProfileRequiredException("Dataset profile is required before generating visualizations.")

        # Compute actual checksum of processed dataset file to verify version integrity
        loader = DatasetLoader(self.session)
        df, load_meta = await loader.load_dataset(processed_dataset.id)

        actual_checksum = load_meta.get("checksum") or processed_dataset.checksum
        expected_checksum = processed_dataset.checksum or actual_checksum

        self.validator.validate_dataset_version(
            source_dataset_id=str(dataset_id),
            processed_dataset_id=str(processed_dataset.id),
            expected_checksum=expected_checksum,
            actual_checksum=actual_checksum,
        )

        # Create VisualizationRun record
        run = VisualizationRun(
            dataset_id=source_dataset.id,
            processed_dataset_id=processed_dataset.id,
            profile_id=profile.id,
            processed_checksum=actual_checksum,
            status="RUNNING",
            started_at=utc_now(),
        )
        run = await self.viz_repo.create_run(run)

        try:
            # 1. Prepare Column Profiles dictionary
            column_profiles_data = [
                {
                    "column_name": col.column_name,
                    "data_type": col.inferred_type,
                    "distinct_count": col.unique_count,
                    "null_count": int(round((col.null_percentage / 100.0) * profile.total_rows)),
                    "null_percentage": col.null_percentage,
                }
                for col in profile.column_profiles
            ]

            # 2. Plan Candidates
            candidates = self.planner.plan_candidates(column_profiles_data, total_rows=len(df))

            # 3. Score & Rank Candidates (Top 12 max)
            ranked_candidates = self.scoring_engine.score_and_rank_candidates(
                candidates, column_profiles_data, total_rows=len(df)
            )

            # 4. Construct VisualizationRecommendation records
            recommendations_to_save: List[VisualizationRecommendation] = []
            for rank_idx, cand in enumerate(ranked_candidates, start=1):
                chart_spec = self.chart_builder.build_chart_spec(
                    chart_type=cand.chart_type,
                    x_column=cand.x_column,
                    y_column=cand.y_column,
                    aggregation=cand.aggregation,
                    time_granularity=cand.time_granularity,
                    title=cand.title,
                    description=cand.description,
                )

                rec = VisualizationRecommendation(
                    run_id=run.id,
                    dataset_id=source_dataset.id,
                    processed_dataset_id=processed_dataset.id,
                    profile_id=profile.id,
                    rank=rank_idx,
                    chart_type=cand.chart_type,
                    title=cand.title,
                    description=cand.description,
                    x_column=cand.x_column,
                    y_column=cand.y_column,
                    aggregation=cand.aggregation,
                    score=cand.base_score,
                    reason=cand.reason,
                    chart_spec=chart_spec,
                )
                recommendations_to_save.append(rec)

            # 5. Persist recommendations & update run status
            saved_recs = await self.viz_repo.save_recommendations(recommendations_to_save)
            run.status = "COMPLETED"
            run.completed_at = utc_now()
            run.recommendation_count = len(saved_recs)
            await self.viz_repo.update_run(run)
            await self.session.commit()

            logger.info(f"Successfully generated {len(saved_recs)} visualization recommendations for dataset {dataset_id}")
            return run, saved_recs

        except Exception as exc:
            logger.error(f"Visualization generation failed for dataset {dataset_id}: {exc}")
            run.status = "FAILED"
            run.error_message = str(exc)
            run.completed_at = utc_now()
            try:
                await self.viz_repo.update_run(run)
                await self.session.commit()
            except Exception:
                await self.session.rollback()

            raise VisualizationException(f"Visualization generation failed: {str(exc)}")

    async def get_visualizations_for_dataset(
        self, dataset_id: uuid.UUID
    ) -> List[VisualizationRecommendation]:
        recs = await self.viz_repo.get_recommendations_for_dataset(dataset_id)
        if recs:
            return recs

        # If no recommendations generated yet, run pipeline automatically
        _, recs = await self.generate_visualizations(dataset_id)
        return recs

    async def get_visualization_data(
        self, dataset_id: uuid.UUID, visualization_id: uuid.UUID
    ) -> Dict[str, Any]:
        rec = await self.viz_repo.get_recommendation_by_id(visualization_id)
        if not rec or rec.dataset_id != dataset_id:
            raise VisualizationNotFoundException(f"Visualization recommendation '{visualization_id}' not found for dataset '{dataset_id}'.")

        if rec.aggregation:
            self.validator.validate_aggregation(rec.aggregation)

        # Load processed dataset
        loader = DatasetLoader(self.session)
        df, _ = await loader.load_dataset(rec.processed_dataset_id)

        chart_payload = self.chart_builder.build_chart_data(df, rec.chart_spec)
        chart_payload["visualization_id"] = str(rec.id)
        chart_payload["title"] = rec.title
        chart_payload["rank"] = rec.rank
        chart_payload["score"] = rec.score
        chart_payload["reason"] = rec.reason

        return chart_payload
