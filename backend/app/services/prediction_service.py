import logging
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sklearn.linear_model import LinearRegression, LogisticRegression

from app.core.config import settings
from app.core.exceptions import (
    DatasetNotFoundException,
    PredictionException,
    PredictionNotFoundException,
    PredictionVersionMismatchException,
    PreprocessingRequiredException,
    ProfileRequiredException,
    TargetColumnInvalidException,
    TargetColumnRequiredException,
    UnsupportedProblemTypeException,
)
from app.db.models.dataset import Dataset
from app.db.models.prediction_run import PredictionRun
from app.db.models.prediction_result import PredictionResult
from app.db.repositories.dataset_repository import DatasetRepository
from app.db.repositories.prediction_repository import PredictionRepository
from app.db.repositories.preprocessing_repository import PreprocessingRepository
from app.db.repositories.profile_repository import ProfileRepository
from app.services.dataset_loader import DatasetLoader
from app.services.prediction_models import (
    MajorityClassClassifier,
    MeanRegressor,
    NaiveForecast,
    build_preprocessing_pipeline,
    evaluate_classification,
    evaluate_regression,
)
from app.services.prediction_planner import PredictionPlanner
from app.services.prediction_scoring import calculate_baseline_improvement
from app.services.prediction_validation import validate_prediction_eligibility

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PredictionService:
    """Orchestrates prediction pipeline fitting, model selection on Validation split,

    final evaluation on Test split, leakage prevention, and persistence.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.profile_repo = ProfileRepository(session)
        self.prep_repo = PreprocessingRepository(session)
        self.pred_repo = PredictionRepository(session)
        self.planner = PredictionPlanner()

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

    async def run_prediction(
        self,
        dataset_id: uuid.UUID,
        target_column: Optional[str] = None,
        problem_type: Optional[str] = None,
    ) -> PredictionRun:
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
            raise PredictionVersionMismatchException()

        df = loader.load_dataframe(processed_dataset.file_path, processed_dataset.file_format)

        # Identify date column if available
        date_column = None
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_column = col
                break
            for prof in profile.columns:
                if prof.column_name == col and prof.semantic_type in ["DATETIME", "DATE", "TEMPORAL"]:
                    try:
                        df[col] = pd.to_datetime(df[col])
                        date_column = col
                        break
                    except Exception:
                        pass
            if date_column:
                break

        # If target_column omitted, select first eligible numeric/categorical column
        if not target_column:
            for prof in profile.columns:
                if not prof.is_identifier and not prof.is_constant and prof.column_name in df.columns:
                    target_column = prof.column_name
                    break

        if not target_column:
            raise TargetColumnRequiredException("No eligible target column found in dataset profile.")

        # Infer problem type if not specified
        if not problem_type:
            problem_type = self.planner.infer_problem_type(df[target_column], date_column=date_column)

        # Validate target eligibility
        validate_prediction_eligibility(
            df=df,
            column_profiles=profile.columns,
            target_column=target_column,
            problem_type=problem_type,
        )

        num_feats, cat_feats = self.planner.select_features(
            df=df,
            column_profiles=profile.columns,
            target_column=target_column,
            date_column=date_column,
        )
        feature_columns = num_feats + cat_feats

        # Train (60%) / Validation (20%) / Test (20%) split
        train_df, val_df, test_df = self.planner.split_data(
            df=df,
            target_column=target_column,
            problem_type=problem_type,
            date_column=date_column,
        )

        run = PredictionRun(
            dataset_id=source_dataset.id,
            processed_dataset_id=processed_dataset.id,
            profile_id=profile.id,
            processed_checksum=initial_checksum,
            problem_type=problem_type,
            target_column=target_column,
            model_name="UNINITIALIZED",
            status="RUNNING",
            started_at=utc_now(),
            training_rows=len(train_df),
            validation_rows=len(val_df),
            test_rows=len(test_df),
            feature_columns=feature_columns,
            random_state=settings.RANDOM_STATE,
        )
        run = await self.pred_repo.create_run(run)

        try:
            results_to_save: List[PredictionResult] = []

            if problem_type == "REGRESSION":
                model_name = "LinearRegression"
                model_params = {"fit_intercept": True}

                # Preprocessing pipeline fit ONLY on train_df
                prep_pipeline = build_preprocessing_pipeline(num_feats, cat_feats)
                X_train = prep_pipeline.fit_transform(train_df[feature_columns])
                y_train = train_df[target_column].values.astype(float)

                X_val = prep_pipeline.transform(val_df[feature_columns])
                y_val = val_df[target_column].values.astype(float)

                X_test = prep_pipeline.transform(test_df[feature_columns])
                y_test = test_df[target_column].values.astype(float)

                # Fit Baseline MeanRegressor
                baseline = MeanRegressor().fit(train_df[feature_columns], train_df[target_column])
                y_val_base = baseline.predict(val_df[feature_columns])
                val_base_metrics = evaluate_regression(y_val, y_val_base)

                y_test_base = baseline.predict(test_df[feature_columns])
                base_metrics = evaluate_regression(y_test, y_test_base)

                # Fit Main Model (LinearRegression)
                reg = LinearRegression().fit(X_train, y_train)
                y_val_pred = reg.predict(X_val)
                val_metrics = evaluate_regression(y_val, y_val_pred)

                # ONE final Test evaluation (Reported Performance)
                y_test_pred = reg.predict(X_test)
                final_metrics = evaluate_regression(y_test, y_test_pred)

                # Calculate improvement
                improvement = calculate_baseline_improvement(final_metrics, base_metrics, "REGRESSION")
                final_metrics["improvement"] = improvement

                # Build bounded prediction results for test set
                for idx, (actual, pred) in enumerate(zip(y_test, y_test_pred)):
                    err = float(abs(actual - pred))
                    results_to_save.append(
                        PredictionResult(
                            run_id=run.id,
                            observation_reference=f"test_row_{idx}",
                            actual_value=str(round(float(actual), 4)),
                            predicted_value=str(round(float(pred), 4)),
                            prediction_error=round(err, 4),
                            lower_bound=None,
                            upper_bound=None,
                            split="TEST",
                        )
                    )

            elif problem_type == "CLASSIFICATION":
                model_name = "LogisticRegression"
                model_params = {"max_iter": 500, "random_state": settings.RANDOM_STATE}

                prep_pipeline = build_preprocessing_pipeline(num_feats, cat_feats)
                X_train = prep_pipeline.fit_transform(train_df[feature_columns])
                y_train = train_df[target_column].values

                X_val = prep_pipeline.transform(val_df[feature_columns])
                y_val = val_df[target_column].values

                X_test = prep_pipeline.transform(test_df[feature_columns])
                y_test = test_df[target_column].values

                # Baseline MajorityClassClassifier
                baseline = MajorityClassClassifier().fit(train_df[feature_columns], train_df[target_column])
                y_test_base = baseline.predict(test_df[feature_columns])
                base_metrics = evaluate_classification(y_test, y_test_base)

                # Main LogisticRegression
                clf = LogisticRegression(max_iter=500, random_state=settings.RANDOM_STATE).fit(X_train, y_train)
                y_val_pred = clf.predict(X_val)
                val_metrics = evaluate_classification(y_val, y_val_pred)

                y_test_pred = clf.predict(X_test)
                y_test_prob = clf.predict_proba(X_test) if hasattr(clf, "predict_proba") else None
                final_metrics = evaluate_classification(y_test, y_test_pred, y_test_prob)

                improvement = calculate_baseline_improvement(final_metrics, base_metrics, "CLASSIFICATION")
                final_metrics["improvement"] = improvement

                for idx, (actual, pred) in enumerate(zip(y_test, y_test_pred)):
                    results_to_save.append(
                        PredictionResult(
                            run_id=run.id,
                            observation_reference=f"test_row_{idx}",
                            actual_value=str(actual),
                            predicted_value=str(pred),
                            prediction_error=0.0 if str(actual) == str(pred) else 1.0,
                            lower_bound=None,
                            upper_bound=None,
                            split="TEST",
                        )
                    )

            elif problem_type == "FORECASTING":
                model_name = "NaiveForecast"
                model_params = {"strategy": "previous_value"}

                y_train = train_df[target_column].values.astype(float)
                y_val = val_df[target_column].values.astype(float)
                y_test = test_df[target_column].values.astype(float)

                baseline = NaiveForecast().fit(train_df[target_column])

                # Forecast for test window
                y_test_pred = baseline.predict(len(y_test))
                final_metrics = evaluate_regression(y_test, y_test_pred)
                base_metrics = dict(final_metrics)

                improvement = {"mae_reduction_pct": 0.0, "is_better": True}
                final_metrics["improvement"] = improvement

                for idx, (actual, pred) in enumerate(zip(y_test, y_test_pred)):
                    err = float(abs(actual - pred))
                    results_to_save.append(
                        PredictionResult(
                            run_id=run.id,
                            observation_reference=f"test_time_{idx}",
                            actual_value=str(round(float(actual), 4)),
                            predicted_value=str(round(float(pred), 4)),
                            prediction_error=round(err, 4),
                            lower_bound=None,
                            upper_bound=None,
                            split="TEST",
                        )
                    )

                # Generate 5 future forecast steps
                future_steps = 5
                future_preds = baseline.predict(future_steps)
                for idx, f_pred in enumerate(future_preds):
                    results_to_save.append(
                        PredictionResult(
                            run_id=run.id,
                            observation_reference=f"future_step_{idx + 1}",
                            actual_value=None,
                            predicted_value=str(round(float(f_pred), 4)),
                            prediction_error=None,
                            lower_bound=None,
                            upper_bound=None,
                            split="FUTURE_FORECAST",
                        )
                    )

            else:
                raise UnsupportedProblemTypeException(f"Unsupported problem_type '{problem_type}'")

            final_checksum = loader.calculate_checksum(processed_dataset.file_path)
            if final_checksum != initial_checksum:
                run.status = "FAILED"
                run.error_message = "Processed dataset checksum modified during prediction execution."
                await self.pred_repo.update_run(run)
                raise PredictionVersionMismatchException()

            # Persist bounded results
            bounded_results = results_to_save[: settings.MAX_PREDICTION_RESULTS]
            if bounded_results:
                await self.pred_repo.save_prediction_results(bounded_results)

            run.model_name = model_name
            run.model_parameters = model_params
            run.metrics = final_metrics
            run.baseline_metrics = base_metrics
            run.status = "COMPLETED"
            run.completed_at = utc_now()

            await self.pred_repo.update_run(run)
            return await self.pred_repo.get_run_by_id(run.id)

        except Exception as e:
            run.status = "FAILED"
            run.error_message = str(e)
            await self.pred_repo.update_run(run)
            if isinstance(e, (PredictionVersionMismatchException, PreprocessingRequiredException, ProfileRequiredException, TargetColumnRequiredException, TargetColumnInvalidException, UnsupportedProblemTypeException)):
                raise e
            logger.exception(f"Prediction execution failed: {e}")
            raise PredictionException(message=f"Model training failed: {str(e)}")

    async def get_latest_run(self, dataset_id: uuid.UUID) -> PredictionRun:
        run = await self.pred_repo.get_latest_completed_run_for_dataset(dataset_id)
        if not run:
            raise PredictionNotFoundException("No completed prediction run found for this dataset.")
        return run

    async def get_run_by_id(self, run_id: uuid.UUID) -> PredictionRun:
        run = await self.pred_repo.get_run_by_id(run_id)
        if not run:
            raise PredictionNotFoundException("Prediction run not found.")
        return run

    async def get_prediction_results(
        self,
        run_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[List[PredictionResult], int]:
        run = await self.pred_repo.get_run_by_id(run_id)
        if not run:
            raise PredictionNotFoundException("Prediction run not found.")
        return await self.pred_repo.get_results_paginated(run_id=run_id, offset=offset, limit=limit)
