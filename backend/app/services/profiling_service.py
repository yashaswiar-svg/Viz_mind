import math
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import VizMindException
from app.core.logging import logger
from app.db.models.dataset_column_profile import DatasetColumnProfile
from app.db.models.dataset_profile import DatasetProfile
from app.db.repositories.profile_repository import ProfileRepository
from app.schemas.profile import (
    DataQualityIssue,
    DatasetColumnProfileResponse,
    DatasetProfileOverview,
    DatasetProfileResponse,
    DatasetQualityResponse,
)
from app.services.data_quality_service import DataQualityService
from app.services.dataset_loader import DatasetLoader


def sanitize_float(val: Any) -> float:
    if val is None or pd.isna(val) or math.isinf(val):
        return None
    return float(val)


class ProfilingService:
    """Service orchestrating read-only dataset profiling and quality engine execution."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.loader = DatasetLoader(session)
        self.repository = ProfileRepository(session)

    @property
    def storage_service(self):
        return self.loader.storage_service

    @storage_service.setter
    def storage_service(self, service):
        self.loader.storage_service = service

    @staticmethod
    def infer_column_type(series: pd.Series) -> str:
        """Deterministically classifies a Pandas Series into a semantic type."""
        dtype_str = str(series.dtype).lower()

        if "bool" in dtype_str:
            return "boolean"
        if "datetime" in dtype_str:
            return "datetime"
        if "int" in dtype_str or "float" in dtype_str:
            return "numeric"

        # Check object / string series
        non_null_series = series.dropna()
        if non_null_series.empty:
            return "text"

        # Check boolean values represented as strings
        unique_vals = set(non_null_series.astype(str).str.strip().str.lower().unique())
        if unique_vals.issubset({"true", "false", "1", "0", "yes", "no"}):
            return "boolean"

        # Check for Datetime parsing
        if series.dtype == object and len(non_null_series) > 0:
            try:
                pd.to_datetime(non_null_series.iloc[:50], errors="raise")
                return "datetime"
            except (ValueError, TypeError):
                pass

        # Check for Categorical vs Text
        unique_count = series.nunique(dropna=True)
        total_count = len(series)
        if unique_count <= 20 or (total_count > 0 and (unique_count / total_count) <= 0.05):
            return "categorical"

        return "text"

    def profile_column(self, series: pd.Series, col_name: str, col_idx: int) -> Dict[str, Any]:
        """Calculates column-level statistical profile."""
        total_rows = len(series)
        null_count = int(series.isna().sum())
        non_null_count = total_rows - null_count
        null_pct = round((null_count / total_rows * 100.0), 2) if total_rows > 0 else 0.0

        unique_count = int(series.nunique(dropna=True))
        unique_pct = round((unique_count / max(non_null_count, 1) * 100.0), 2) if non_null_count > 0 else 0.0
        is_constant = bool(unique_count == 1 and non_null_count > 0)

        inferred_type = self.infer_column_type(series)

        col_dict = {
            "column_name": col_name,
            "column_index": col_idx,
            "inferred_type": inferred_type,
            "pandas_dtype": str(series.dtype),
            "null_count": null_count,
            "null_percentage": null_pct,
            "non_null_count": non_null_count,
            "unique_count": unique_count,
            "unique_percentage": unique_pct,
            "is_constant": is_constant,
            "min_value": None,
            "max_value": None,
            "mean_value": None,
            "median_value": None,
            "std_value": None,
            "q1_value": None,
            "q3_value": None,
            "top_values": None,
            "min_length": None,
            "max_length": None,
            "avg_length": None,
            "min_datetime": None,
            "max_datetime": None,
            "true_count": None,
            "false_count": None,
        }

        # Type-specific statistical extraction
        if inferred_type == "numeric" and non_null_count > 0:
            numeric_series = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            if not numeric_series.empty:
                col_dict["min_value"] = sanitize_float(numeric_series.min())
                col_dict["max_value"] = sanitize_float(numeric_series.max())
                col_dict["mean_value"] = sanitize_float(numeric_series.mean())
                col_dict["median_value"] = sanitize_float(numeric_series.median())
                col_dict["std_value"] = sanitize_float(numeric_series.std())
                col_dict["q1_value"] = sanitize_float(numeric_series.quantile(0.25))
                col_dict["q3_value"] = sanitize_float(numeric_series.quantile(0.75))

        elif inferred_type == "categorical" and non_null_count > 0:
            vc = series.value_counts(dropna=True).head(10)
            top_list = []
            for val, count in vc.items():
                pct = round((count / non_null_count * 100.0), 2)
                top_list.append({"value": str(val), "count": int(count), "percentage": pct})
            col_dict["top_values"] = top_list

        elif inferred_type == "text" and non_null_count > 0:
            str_series = series.dropna().astype(str)
            lengths = str_series.str.len()
            col_dict["min_length"] = int(lengths.min())
            col_dict["max_length"] = int(lengths.max())
            col_dict["avg_length"] = round(float(lengths.mean()), 1)

            vc = series.value_counts(dropna=True).head(5)
            top_list = []
            for val, count in vc.items():
                pct = round((count / non_null_count * 100.0), 2)
                top_list.append({"value": str(val)[:50], "count": int(count), "percentage": pct})
            col_dict["top_values"] = top_list

        elif inferred_type == "datetime" and non_null_count > 0:
            dt_series = pd.to_datetime(series, errors="coerce").dropna()
            if not dt_series.empty:
                col_dict["min_datetime"] = dt_series.min().isoformat()
                col_dict["max_datetime"] = dt_series.max().isoformat()

        elif inferred_type == "boolean" and non_null_count > 0:
            str_series = series.dropna().astype(str).str.strip().str.lower()
            true_cnt = int(str_series.isin(["true", "1", "yes"]).sum())
            false_cnt = int(str_series.isin(["false", "0", "no"]).sum())
            col_dict["true_count"] = true_cnt
            col_dict["false_count"] = false_cnt

        return col_dict

    async def profile_dataset(self, dataset_id: uuid.UUID) -> DatasetProfileResponse:
        logger.info(f"Starting profiling execution for dataset {dataset_id}")

        # 1. Load DataFrame safely using DatasetLoader
        df, sheet_name = await self.loader.load_dataset(dataset_id)

        # 2. Compute overview metrics
        row_count = len(df)
        column_count = len(df.columns)
        total_cells = max(row_count * column_count, 1)

        missing_cells = int(df.isna().sum().sum())
        missing_cell_pct = round((missing_cells / total_cells * 100.0), 2)

        duplicate_rows = int(df.duplicated().sum())
        duplicate_row_pct = round((duplicate_rows / max(row_count, 1) * 100.0), 2) if row_count > 0 else 0.0

        memory_bytes = int(df.memory_usage(deep=True).sum())

        # 3. Column-level profiling
        column_profile_dicts = []
        for idx, col_name in enumerate(df.columns):
            col_profile = self.profile_column(df[col_name], str(col_name), idx)
            column_profile_dicts.append(col_profile)

        # 4. Data Quality Engine execution
        quality_score, quality_level, issues = DataQualityService.evaluate_quality(
            row_count=row_count,
            column_count=column_count,
            duplicate_rows=duplicate_rows,
            missing_cells=missing_cells,
            column_profiles=column_profile_dicts,
        )

        issues_json = [issue.model_dump() for issue in issues]

        # 5. Build ORM Models
        now = datetime.now(timezone.utc)
        profile_orm = DatasetProfile(
            id=uuid.uuid4(),
            dataset_id=dataset_id,
            row_count=row_count,
            column_count=column_count,
            duplicate_row_count=duplicate_rows,
            duplicate_row_percentage=duplicate_row_pct,
            missing_cell_count=missing_cells,
            missing_cell_percentage=missing_cell_pct,
            memory_usage_bytes=memory_bytes,
            sheet_name=sheet_name,
            quality_score=quality_score,
            quality_level=quality_level,
            quality_issues=issues_json,
            profiled_at=now,
            created_at=now,
            updated_at=now,
        )

        column_orms = []
        for col_dict in column_profile_dicts:
            col_orm = DatasetColumnProfile(
                id=uuid.uuid4(),
                column_name=col_dict["column_name"],
                column_index=col_dict["column_index"],
                inferred_type=col_dict["inferred_type"],
                pandas_dtype=col_dict["pandas_dtype"],
                null_count=col_dict["null_count"],
                null_percentage=col_dict["null_percentage"],
                non_null_count=col_dict["non_null_count"],
                unique_count=col_dict["unique_count"],
                unique_percentage=col_dict["unique_percentage"],
                is_constant=col_dict["is_constant"],
                min_value=col_dict["min_value"],
                max_value=col_dict["max_value"],
                mean_value=col_dict["mean_value"],
                median_value=col_dict["median_value"],
                std_value=col_dict["std_value"],
                q1_value=col_dict["q1_value"],
                q3_value=col_dict["q3_value"],
                top_values=col_dict["top_values"],
                min_length=col_dict["min_length"],
                max_length=col_dict["max_length"],
                avg_length=col_dict["avg_length"],
                min_datetime=col_dict["min_datetime"],
                max_datetime=col_dict["max_datetime"],
                true_count=col_dict["true_count"],
                false_count=col_dict["false_count"],
            )
            column_orms.append(col_orm)

        # 6. Save atomically using ProfileRepository
        try:
            saved_profile = await self.repository.save_profile(profile_orm, column_orms)
            logger.info(f"Successfully saved profile for dataset {dataset_id}")
            return self._build_response(saved_profile)
        except Exception as exc:
            logger.error(f"Failed to persist profile for dataset {dataset_id}: {exc}")
            raise VizMindException(f"Profile persistence failed: {str(exc)}", code="DATABASE_ERROR")

    async def get_profile(self, dataset_id: uuid.UUID) -> DatasetProfileResponse:
        profile = await self.repository.get_by_dataset_id(dataset_id)
        if not profile:
            raise VizMindException(
                f"No profile found for dataset {dataset_id}.",
                code="PROFILE_NOT_FOUND",
                status_code=404,
            )
        return self._build_response(profile)

    def _build_response(self, profile: DatasetProfile) -> DatasetProfileResponse:
        overview = DatasetProfileOverview(
            rows=profile.row_count,
            columns=profile.column_count,
            duplicate_rows=profile.duplicate_row_count,
            duplicate_row_percentage=profile.duplicate_row_percentage,
            missing_cells=profile.missing_cell_count,
            missing_cell_percentage=profile.missing_cell_percentage,
            memory_bytes=profile.memory_usage_bytes,
            sheet_name=profile.sheet_name,
        )

        issues = [DataQualityIssue(**iss) for iss in (profile.quality_issues or [])]
        quality = DatasetQualityResponse(
            score=profile.quality_score,
            level=profile.quality_level,
            issues=issues,
        )

        col_responses = [DatasetColumnProfileResponse.model_validate(c) for c in profile.columns]

        return DatasetProfileResponse(
            id=profile.id,
            dataset_id=profile.dataset_id,
            profiled_at=profile.profiled_at,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            overview=overview,
            quality=quality,
            columns=col_responses,
        )
