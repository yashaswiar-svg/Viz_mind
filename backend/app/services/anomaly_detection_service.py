import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    AnomalyDetectionException,
    AnomalyNotFoundException,
    AnomalyVersionMismatchException,
    DatasetNotFoundException,
    PreprocessingRequiredException,
    ProfileRequiredException,
)
from app.db.models.anomaly_detection_run import AnomalyDetectionRun
from app.db.models.anomaly_result import AnomalyResult
from app.db.models.dataset import Dataset
from app.db.repositories.anomaly_detection_repository import AnomalyDetectionRepository
from app.db.repositories.dataset_repository import DatasetRepository
from app.db.repositories.preprocessing_repository import PreprocessingRepository
from app.db.repositories.profile_repository import ProfileRepository
from app.services.anomaly_detection_planner import AnomalyDetectionPlanner
from app.services.anomaly_scoring import calculate_anomaly_score_and_severity
from app.services.anomaly_statistics import (
    detect_iqr_anomalies,
    detect_robust_zscore_anomalies,
    detect_time_series_rolling_anomalies,
)
from app.services.dataset_loader import DatasetLoader

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AnomalyDetectionService:
    """Orchestrates anomaly detection execution, version validation, deduplication, scoring, and persistence."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.profile_repo = ProfileRepository(session)
        self.prep_repo = PreprocessingRepository(session)
        self.anomaly_repo = AnomalyDetectionRepository(session)
        self.planner = AnomalyDetectionPlanner()

    async def get_processed_dataset(self, source_dataset: Dataset) -> Dataset:
        if source_dataset.dataset_kind == "PROCESSED":
            return source_dataset

        prep_job = await self.prep_repo.get_latest_job_for_dataset(source_dataset.id)
        if not prep_job or not prep_job.output_dataset_id or prep_job.status != "COMPLETED":
            raise PreprocessingRequiredException()

        processed_dataset = await self.dataset_repo.get_by_id(prep_job.output_dataset_id)
        if not processed_dataset:
            raise PreprocessingRequiredException()

        return processed_dataset

    async def run_anomaly_detection(
        self,
        dataset_id: uuid.UUID,
        method: Optional[str] = None,
    ) -> AnomalyDetectionRun:
        source_dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not source_dataset:
            raise DatasetNotFoundException()

        profile = await self.profile_repo.get_by_dataset_id(source_dataset.id)
        if not profile:
            raise ProfileRequiredException()

        processed_dataset = await self.get_processed_dataset(source_dataset)

        loader = DatasetLoader()
        initial_checksum = loader.calculate_checksum(processed_dataset.file_path)
        if processed_dataset.file_checksum and initial_checksum != processed_dataset.file_checksum:
            raise AnomalyVersionMismatchException()

        df = loader.load_dataframe(processed_dataset.file_path, processed_dataset.file_format)
        total_observations = len(df)

        plan = self.planner.plan_analysis(
            df=df,
            column_profiles=profile.columns,
            requested_method=method,
        )

        run = AnomalyDetectionRun(
            dataset_id=source_dataset.id,
            processed_dataset_id=processed_dataset.id,
            profile_id=profile.id,
            processed_checksum=initial_checksum,
            method=method or "UNIVARIATE_COMBINED",
            status="RUNNING",
            started_at=utc_now(),
            total_observations=total_observations,
        )
        run = await self.anomaly_repo.create_run(run)

        raw_candidates = []
        try:
            for task in plan["tasks"]:
                col = task["column"]
                task_method = task["method"]

                if task_method == "IQR":
                    res = detect_iqr_anomalies(df[col])
                elif task_method == "ROBUST_ZSCORE":
                    res = detect_robust_zscore_anomalies(df[col])
                elif task_method == "TIME_SERIES_RESIDUAL":
                    res = detect_time_series_rolling_anomalies(
                        df, date_col=task["date_column"], num_col=col
                    )
                else:
                    res = []

                for item in res:
                    item["column_name"] = col
                    raw_candidates.append(item)

            merged_anomalies = calculate_anomaly_score_and_severity(raw_candidates)
            total_detected = len(merged_anomalies)

            # Limit output to MAX_ANOMALY_RESULTS
            results_truncated = total_detected > settings.MAX_ANOMALY_RESULTS
            bounded_anomalies = merged_anomalies[: settings.MAX_ANOMALY_RESULTS]

            final_checksum = loader.calculate_checksum(processed_dataset.file_path)
            if final_checksum != initial_checksum:
                run.status = "FAILED"
                run.error_message = "Processed dataset checksum modified during anomaly detection execution."
                await self.anomaly_repo.update_run(run)
                raise AnomalyVersionMismatchException()

            db_results = []
            for item in bounded_anomalies:
                res_obj = AnomalyResult(
                    run_id=run.id,
                    dataset_id=source_dataset.id,
                    processed_dataset_id=processed_dataset.id,
                    observation_reference=item["observation_reference"],
                    column_name=item["column_name"],
                    value=item["value"],
                    expected_range=item["expected_range"],
                    anomaly_score=item["anomaly_score"],
                    severity=item["severity"],
                    methods_detected=item["methods_detected"],
                    evidence=item["evidence"],
                    statistics=item["statistics"],
                )
                db_results.append(res_obj)

            if db_results:
                await self.anomaly_repo.save_anomaly_results(db_results)

            anomaly_pct = (total_detected / total_observations * 100.0) if total_observations > 0 else 0.0

            run.status = "COMPLETED"
            run.completed_at = utc_now()
            run.anomaly_count = total_detected
            run.anomaly_percentage = round(anomaly_pct, 2)
            run.results_truncated = results_truncated
            run.method_summary = {
                "eligible_columns_count": len(plan["eligible_columns"]),
                "tasks_count": len(plan["tasks"]),
                "raw_candidates_count": len(raw_candidates),
                "total_detected": total_detected,
                "returned_count": len(bounded_anomalies),
            }

            await self.anomaly_repo.update_run(run)
            return await self.anomaly_repo.get_run_by_id(run.id)

        except Exception as e:
            run.status = "FAILED"
            run.error_message = str(e)
            await self.anomaly_repo.update_run(run)
            if isinstance(e, (AnomalyVersionMismatchException, PreprocessingRequiredException, ProfileRequiredException)):
                raise e
            logger.exception(f"Anomaly detection failed: {e}")
            raise AnomalyDetectionException(message=f"Anomaly detection execution failed: {str(e)}")

    async def get_latest_run(self, dataset_id: uuid.UUID) -> AnomalyDetectionRun:
        run = await self.anomaly_repo.get_latest_completed_run_for_dataset(dataset_id)
        if not run:
            raise AnomalyNotFoundException("No completed anomaly detection run found for this dataset.")
        return run

    async def get_anomaly_by_id(self, anomaly_id: uuid.UUID) -> AnomalyResult:
        result = await self.anomaly_repo.get_anomaly_by_id(anomaly_id)
        if not result:
            raise AnomalyNotFoundException("Anomaly result not found.")
        return result
