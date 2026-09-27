import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DatasetNotFoundException,
    PreprocessingException,
    PreprocessingNotFoundException,
    ProfileRequiredException,
)
from app.core.logging import logger
from app.db.models.dataset import Dataset
from app.db.models.preprocessing_job import PreprocessingJob
from app.db.models.preprocessing_transformation import PreprocessingTransformation
from app.db.repositories.dataset_repository import DatasetRepository
from app.db.repositories.profile_repository import ProfileRepository
from app.db.repositories.preprocessing_repository import PreprocessingRepository
from app.services.dataset_loader import DatasetLoader
from app.services.preprocessing_planner import PreprocessingPlanner
from app.services.preprocessing_transformers import PreprocessingTransformers
from app.services.storage_service import StorageService


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PreprocessingService:
    """Service orchestrating dataset preprocessing workflow, derived dataset creation, and source integrity verification."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.profile_repo = ProfileRepository(session)
        self.prep_repo = PreprocessingRepository(session)
        self.storage_service = StorageService()

    async def get_latest_preprocessing_report(self, dataset_id: uuid.UUID) -> Tuple[PreprocessingJob, Dataset, List[PreprocessingTransformation]]:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise DatasetNotFoundException(f"Dataset with ID {dataset_id} not found.")

        job = await self.prep_repo.get_latest_job_for_dataset(dataset_id)
        if not job:
            raise PreprocessingNotFoundException("No preprocessing report found for this dataset.")

        output_dataset = None
        if job.output_dataset_id:
            output_dataset = await self.dataset_repo.get_by_id(job.output_dataset_id)

        transformations = await self.prep_repo.get_transformations_for_job(job.id)
        return job, output_dataset, transformations

    async def run_preprocessing(
        self, dataset_id: uuid.UUID, config: Dict[str, Any] = None
    ) -> Tuple[PreprocessingJob, Dataset, List[PreprocessingTransformation]]:
        # 1. Verify source dataset exists
        source_dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not source_dataset:
            raise DatasetNotFoundException(f"Dataset with ID {dataset_id} not found.")

        # 2. Verify Phase 3 profile exists
        profile = await self.profile_repo.get_profile_by_dataset_id(dataset_id)
        if not profile:
            raise ProfileRequiredException("Phase 3 dataset profile is required before running preprocessing.")


        # Construct profile dictionary format for planner
        profile_data = {
            "columns": [
                {
                    "column_name": col.column_name,
                    "inferred_type": col.inferred_type,
                    "null_percentage": col.null_percentage,
                    "unique_count": col.unique_count,
                    "is_constant": col.is_constant,
                }
                for col in profile.column_profiles
            ]
        }

        # 3. Load source dataset & record initial checksum
        loader = DatasetLoader(self.session)
        df, load_meta = await loader.load_dataset(dataset_id)

        source_checksum_before = source_dataset.checksum or load_meta.get("checksum")

        # 4. Create PreprocessingJob record
        job = PreprocessingJob(
            dataset_id=dataset_id,
            source_profile_id=profile.id,
            status="RUNNING",
            started_at=utc_now(),
            rows_before=len(df),
            columns_before=len(df.columns),
            missing_cells_before=int(df.isna().sum().sum()),
            duplicate_rows_before=int(df.duplicated().sum()),
            source_checksum_before=source_checksum_before,
        )
        job = await self.prep_repo.create_job(job)

        processed_dataset_id = uuid.uuid4()
        transformations_to_save: List[PreprocessingTransformation] = []

        try:
            # 5. Build Preprocessing Plan
            planner = PreprocessingPlanner(config=config)
            plan_steps = planner.build_plan(df, profile_data)

            # 6. Execute Transformations
            step_counter = 1
            for step in plan_steps:
                ttype = step["transformation_type"]
                col_name = step.get("column_name")

                rows_aff = 0
                vals_aff = 0
                desc = step.get("reason", "")
                params = step.get("parameters", {})

                if ttype == "REMOVE_DUPLICATES":
                    df, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.remove_duplicates(df)
                    params.update(meta)
                elif ttype == "DROP_EMPTY_COLUMN":
                    df, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.drop_empty_columns(df)
                    params.update(meta)
                elif ttype == "DROP_CONSTANT_COLUMN":
                    df, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.drop_constant_columns(df)
                    params.update(meta)
                elif ttype == "IMPUTE_MISSING_NUMERIC" and col_name in df.columns:
                    df, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.impute_missing_numeric(df, col_name)
                    params.update(meta)
                elif ttype == "IMPUTE_MISSING_CATEGORICAL" and col_name in df.columns:
                    df, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.impute_missing_categorical(df, col_name)
                    params.update(meta)
                elif ttype == "IMPUTE_MISSING_TEXT" and col_name in df.columns:
                    df, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.impute_missing_text(df, col_name)
                    params.update(meta)
                elif ttype == "NORMALIZE_TEXT" and col_name in df.columns:
                    df, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.normalize_text_whitespace(df, col_name)
                    params.update(meta)
                elif ttype == "ONE_HOT_ENCODING" and col_name in df.columns:
                    df, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.one_hot_encode_categorical(df, col_name)
                    params.update(meta)
                elif ttype == "SCALE_NUMERIC" and col_name in df.columns:
                    df, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.scale_numeric_standard(df, col_name)
                    params.update(meta)

                trans = PreprocessingTransformation(
                    job_id=job.id,
                    step_order=step_counter,
                    transformation_type=ttype,
                    column_name=col_name,
                    parameters=params,
                    rows_affected=rows_aff,
                    values_affected=vals_aff,
                    description=desc,
                )
                transformations_to_save.append(trans)
                step_counter += 1

            # 7. Post-transformation stats & source file checksum integrity check
            file_path = self.storage_service.get_dataset_dir(dataset_id)
            source_file = next(file_path.glob("*"), None)
            if source_file and source_file.exists():
                hasher = hashlib.sha256()
                with open(source_file, "rb") as sf:
                    while chunk := sf.read(1024 * 1024):
                        hasher.update(chunk)
                source_checksum_after = hasher.hexdigest()
            else:
                source_checksum_after = source_checksum_before

            if source_checksum_before and source_checksum_after:
                assert source_checksum_before == source_checksum_after, "CRITICAL: Source dataset checksum altered during preprocessing!"

            # 8. Save Processed DataFrame to disk
            logical_path, proc_checksum, proc_size = self.storage_service.save_processed_dataframe(
                df, processed_dataset_id, source_dataset.file_type
            )

            # 9. Create Processed Dataset record
            processed_dataset = Dataset(
                id=processed_dataset_id,
                parent_dataset_id=source_dataset.id,
                dataset_kind="PROCESSED",
                name=f"{source_dataset.name} (Processed)",
                original_filename=source_dataset.original_filename,
                file_type=source_dataset.file_type,
                file_size=proc_size,
                storage_path=logical_path,
                checksum=proc_checksum,
                status="ready",
            )
            processed_dataset = await self.dataset_repo.create(processed_dataset)

            # 10. Update Job status
            job.output_dataset_id = processed_dataset.id
            job.status = "COMPLETED"
            job.completed_at = utc_now()
            job.rows_after = len(df)
            job.columns_after = len(df.columns)
            job.missing_cells_after = int(df.isna().sum().sum())
            job.duplicate_rows_after = int(df.duplicated().sum())
            job.source_checksum_after = source_checksum_after
            job.processed_checksum = proc_checksum

            await self.prep_repo.update_job(job)
            await self.prep_repo.save_transformations(transformations_to_save)
            await self.session.commit()

            logger.info(f"Successfully completed preprocessing job {job.id} for dataset {dataset_id}")
            return job, processed_dataset, transformations_to_save

        except Exception as exc:
            logger.error(f"Preprocessing failed for dataset {dataset_id}: {exc}")
            self.storage_service.cleanup_dataset_storage(processed_dataset_id)

            job.status = "FAILED"
            job.error_message = str(exc)
            job.completed_at = utc_now()
            try:
                await self.prep_repo.update_job(job)
                await self.session.commit()
            except Exception:
                await self.session.rollback()

            raise PreprocessingException(f"Preprocessing execution failed: {str(exc)}")

