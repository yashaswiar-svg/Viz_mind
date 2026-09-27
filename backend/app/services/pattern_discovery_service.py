import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DatasetNotFoundException,
    PatternDiscoveryException,
    PatternNotFoundException,
    PatternVersionMismatchException,
    PreprocessingRequiredException,
    ProfileRequiredException,
)
from app.db.models.dataset import Dataset
from app.db.models.pattern_discovery_run import PatternDiscoveryRun
from app.db.models.pattern_result import PatternResult
from app.db.repositories.dataset_repository import DatasetRepository
from app.db.repositories.pattern_discovery_repository import PatternDiscoveryRepository
from app.db.repositories.preprocessing_repository import PreprocessingRepository
from app.db.repositories.profile_repository import ProfileRepository
from app.services.dataset_loader import DatasetLoader
from app.services.pattern_discovery_planner import PatternDiscoveryPlanner, FDR_ALPHA
from app.services.pattern_scoring import PatternScoringEngine
from app.services.pattern_statistics import (
    apply_fdr_correction,
    compute_categorical_association,
    compute_correlation,
    compute_distribution_statistics,
    compute_group_difference,
    compute_time_trend,
)
from app.services.pattern_validator import PatternValidator

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PatternDiscoveryService:
    """Orchestrates pattern discovery execution, statistical analyses, FDR correction, scoring, and persistence."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.profile_repo = ProfileRepository(session)
        self.prep_repo = PreprocessingRepository(session)
        self.pattern_repo = PatternDiscoveryRepository(session)
        self.planner = PatternDiscoveryPlanner()
        self.scoring_engine = PatternScoringEngine()
        self.validator = PatternValidator()

    async def get_processed_dataset(self, source_dataset: Dataset) -> Dataset:
        if source_dataset.dataset_kind == "PROCESSED":
            return source_dataset

        prep_job = await self.prep_repo.get_latest_job_for_dataset(source_dataset.id)
        if not prep_job or not prep_job.output_dataset_id or prep_job.status != "COMPLETED":
            raise PreprocessingRequiredException(
                f"Dataset '{source_dataset.id}' has not been preprocessed. Phase 4 preprocessing is required before discovering patterns."
            )

        processed_dataset = await self.dataset_repo.get_by_id(prep_job.output_dataset_id)
        if not processed_dataset:
            raise PreprocessingRequiredException("Processed dataset record not found.")

        return processed_dataset

    async def run_pattern_discovery(
        self, dataset_id: uuid.UUID
    ) -> Tuple[PatternDiscoveryRun, List[PatternResult]]:
        source_dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not source_dataset:
            raise DatasetNotFoundException(f"Dataset with ID {dataset_id} not found.")

        processed_dataset = await self.get_processed_dataset(source_dataset)
        profile = await self.profile_repo.get_profile_by_dataset_id(dataset_id)
        if not profile:
            raise ProfileRequiredException("Dataset profile is required before discovering patterns.")

        # Load processed dataset and get actual checksum
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

        # Create PatternDiscoveryRun
        run = PatternDiscoveryRun(
            dataset_id=source_dataset.id,
            processed_dataset_id=processed_dataset.id,
            profile_id=profile.id,
            processed_checksum=actual_checksum,
            status="RUNNING",
            started_at=utc_now(),
        )
        run = await self.pattern_repo.create_run(run)

        try:
            # 1. Prepare Column Profiles list
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

            # 2. Generate Candidate Tasks
            candidate_tasks = self.planner.generate_candidate_tasks(column_profiles_data, total_rows=len(df))

            # Group candidate tasks by family for statistical processing and FDR correction
            family_raw_results: Dict[str, List[Dict[str, Any]]] = {
                "CORRELATION": [],
                "GROUP_DIFFERENCE": [],
                "CATEGORICAL_ASSOCIATION": [],
                "TIME_TREND": [],
                "DISTRIBUTION": [],
            }

            for task in candidate_tasks:
                ptype = task.pattern_type
                if ptype == "CORRELATION":
                    col1, col2 = task.columns[0], task.columns[1]
                    res = compute_correlation(df[col1], df[col2], method=task.method)
                    if res:
                        res.update({
                            "pattern_type": ptype,
                            "columns": [col1, col2],
                        })
                        family_raw_results["CORRELATION"].append(res)

                elif ptype == "GROUP_DIFFERENCE":
                    g_col, m_col = task.group_column, task.measure_column
                    if g_col and m_col:
                        res = compute_group_difference(df[g_col], df[m_col])
                        if res:
                            res.update({
                                "pattern_type": ptype,
                                "columns": [g_col, m_col],
                            })
                            family_raw_results["GROUP_DIFFERENCE"].append(res)

                elif ptype == "CATEGORICAL_ASSOCIATION":
                    c1, c2 = task.columns[0], task.columns[1]
                    res = compute_categorical_association(df[c1], df[c2])
                    if res:
                        res.update({
                            "pattern_type": ptype,
                            "columns": [c1, c2],
                        })
                        family_raw_results["CATEGORICAL_ASSOCIATION"].append(res)

                elif ptype == "TIME_TREND":
                    dt_col, m_col = task.datetime_column, task.measure_column
                    if dt_col and m_col:
                        res = compute_time_trend(df[dt_col], df[m_col])
                        if res:
                            res.update({
                                "pattern_type": ptype,
                                "columns": [dt_col, m_col],
                            })
                            family_raw_results["TIME_TREND"].append(res)

                elif ptype == "DISTRIBUTION":
                    m_col = task.measure_column
                    if m_col:
                        res = compute_distribution_statistics(df[m_col])
                        if res:
                            res.update({
                                "pattern_type": ptype,
                                "columns": [m_col],
                            })
                            family_raw_results["DISTRIBUTION"].append(res)

            # 3. Apply Benjamini-Hochberg FDR correction per hypothesis family
            all_processed_items: List[Dict[str, Any]] = []

            for family_name, items in family_raw_results.items():
                if not items:
                    continue

                if family_name == "DISTRIBUTION":
                    for item in items:
                        item["raw_p_value"] = None
                        item["adjusted_p_value"] = None
                        item["significant"] = False
                        all_processed_items.append(item)
                else:
                    raw_pvals = [item["raw_p_value"] for item in items]
                    adj_pvals = apply_fdr_correction(raw_pvals)

                    for item, adj_p in zip(items, adj_pvals):
                        item["adjusted_p_value"] = adj_p
                        item["significant"] = bool(adj_p < FDR_ALPHA)
                        all_processed_items.append(item)

            # 4. Score, Deduplicate, and Rank Patterns
            ranked_patterns = self.scoring_engine.score_and_rank_patterns(all_processed_items)

            # 5. Build PatternResult database records
            results_to_save: List[PatternResult] = []
            for item in ranked_patterns:
                # Remove unneeded metadata from statistics JSONB payload
                stats_payload = dict(item.get("statistics", {}))
                for k in ["statistics", "pattern_type", "columns", "rank", "score", "title", "description", "significant", "strength", "sample_size", "raw_p_value", "adjusted_p_value", "effect_size", "method"]:
                    if k in item:
                        stats_payload[k] = item[k]

                res_rec = PatternResult(
                    run_id=run.id,
                    dataset_id=source_dataset.id,
                    processed_dataset_id=processed_dataset.id,
                    pattern_type=item["pattern_type"],
                    rank=item["rank"],
                    score=item["score"],
                    title=item["title"],
                    description=item.get("description"),
                    columns=item["columns"],
                    statistics=stats_payload,
                    significant=item.get("significant", False),
                    strength=item.get("strength", "WEAK"),
                    sample_size=item.get("sample_size", 0),
                    raw_p_value=item.get("raw_p_value"),
                    adjusted_p_value=item.get("adjusted_p_value"),
                    effect_size=item.get("effect_size"),
                    method=item.get("method", "statistical_test"),
                )
                results_to_save.append(res_rec)

            # 6. Re-verify checksum integrity post analysis
            _, post_meta = await loader.load_dataset(processed_dataset.id)
            post_checksum = post_meta.get("checksum") or processed_dataset.checksum
            self.validator.validate_dataset_version(
                source_dataset_id=str(dataset_id),
                processed_dataset_id=str(processed_dataset.id),
                expected_checksum=actual_checksum,
                actual_checksum=post_checksum,
            )

            # 7. Persist results and complete run
            saved_results = await self.pattern_repo.save_pattern_results(results_to_save)
            run.status = "COMPLETED"
            run.completed_at = utc_now()
            run.pattern_count = len(saved_results)
            await self.pattern_repo.update_run(run)
            await self.session.commit()

            logger.info(f"Successfully discovered {len(saved_results)} patterns for dataset {dataset_id}")
            return run, saved_results

        except Exception as exc:
            logger.error(f"Pattern discovery failed for dataset {dataset_id}: {exc}")
            run.status = "FAILED"
            run.error_message = str(exc)
            run.completed_at = utc_now()
            try:
                await self.pattern_repo.update_run(run)
                await self.session.commit()
            except Exception:
                await self.session.rollback()

            raise PatternDiscoveryException(f"Pattern discovery failed: {str(exc)}")

    async def get_latest_patterns_for_dataset(
        self,
        dataset_id: uuid.UUID,
        pattern_type: Optional[str] = None,
        strength: Optional[str] = None,
        significant: Optional[bool] = None,
    ) -> Tuple[Optional[PatternDiscoveryRun], List[PatternResult]]:
        latest_run = await self.pattern_repo.get_latest_completed_run_for_dataset(dataset_id)
        if not latest_run:
            return None, []

        patterns = await self.pattern_repo.get_patterns_for_run(latest_run.id)

        # Apply in-memory filtering if requested
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type.upper() == pattern_type.upper()]
        if strength:
            patterns = [p for p in patterns if p.strength.upper() == strength.upper()]
        if significant is not None:
            patterns = [p for p in patterns if p.significant == significant]

        return latest_run, patterns

    async def get_pattern_by_id(
        self, dataset_id: uuid.UUID, pattern_id: uuid.UUID
    ) -> PatternResult:
        pattern = await self.pattern_repo.get_pattern_by_id(pattern_id)
        if not pattern or pattern.dataset_id != dataset_id:
            raise PatternNotFoundException(f"Discovered pattern '{pattern_id}' not found for dataset '{dataset_id}'.")
        return pattern
