import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.models.dataset import Dataset
from app.db.models.dataset_profile import DatasetProfile
from app.db.models.visualization_run import VisualizationRun
from app.db.models.visualization_recommendation import VisualizationRecommendation
from app.db.models.pattern_discovery_run import PatternDiscoveryRun
from app.db.models.pattern_result import PatternResult
from app.db.models.anomaly_detection_run import AnomalyDetectionRun
from app.db.models.anomaly_result import AnomalyResult
from app.db.models.prediction_run import PredictionRun
from app.services.insight_evidence import EvidenceItem

logger = logging.getLogger(__name__)


class InsightVersionMismatchError(Exception):
    """Raised when analytical results do not match current dataset processed checksum."""
    pass


class InsightEvidenceService:
    """Service for collecting and normalizing grounded analytical evidence from Phases 3-7."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def collect_evidence(
        self,
        dataset: Dataset,
        processed_dataset: Dataset,
        profile: DatasetProfile,
    ) -> Tuple[List[EvidenceItem], str]:
        """
        Collects, validates, and normalizes evidence items across Phases 3-7.
        Returns (evidence_items, processed_checksum).
        """
        processed_checksum = processed_dataset.processed_checksum or ""
        evidence_items: List[EvidenceItem] = []
        counter = 1

        # Helper to format evidence ID
        def next_id() -> str:
            nonlocal counter
            eid = f"EVID_{counter:03d}"
            counter += 1
            return eid

        # 1. Phase 3 Evidence — Profile & Quality Metrics
        profile_evid = await self._collect_phase3_evidence(profile, next_id)
        evidence_items.extend(profile_evid[: settings.MAX_PROFILE_EVIDENCE])

        # 2. Phase 5 Evidence — Visualizations
        viz_evid = await self._collect_phase5_evidence(processed_dataset.id, processed_checksum, next_id)
        evidence_items.extend(viz_evid[: settings.MAX_VISUALIZATION_EVIDENCE])

        # 3. Phase 6 Evidence — Patterns (Correlations, Differences, Trends, Distributions)
        pattern_evid = await self._collect_phase6_evidence(processed_dataset.id, processed_checksum, next_id)
        evidence_items.extend(pattern_evid[: settings.MAX_PATTERN_EVIDENCE])

        # 4. Phase 7 Evidence — Anomalies
        anomaly_evid = await self._collect_phase7_anomaly_evidence(processed_dataset.id, processed_checksum, next_id)
        evidence_items.extend(anomaly_evid[: settings.MAX_ANOMALY_EVIDENCE])

        # 5. Phase 7 Evidence — Predictions & Forecasting
        prediction_evid = await self._collect_phase7_prediction_evidence(processed_dataset.id, processed_checksum, next_id)
        evidence_items.extend(prediction_evid[: settings.MAX_PREDICTION_EVIDENCE])

        # Enforce global total limit
        final_items = evidence_items[: settings.MAX_TOTAL_EVIDENCE_ITEMS]
        logger.info(
            f"Collected {len(final_items)} evidence items for dataset {dataset.id} (processed={processed_dataset.id})"
        )
        return final_items, processed_checksum

    async def _collect_phase3_evidence(
        self, profile: DatasetProfile, next_id_fn: Any
    ) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        # Data quality score evidence
        if profile.overall_quality_score is not None:
            items.append(
                EvidenceItem(
                    evidence_id=next_id_fn(),
                    source_phase="PHASE3_PROFILE",
                    source_type="DATA_QUALITY",
                    source_id=str(profile.id),
                    columns=[],
                    metrics={
                        "overall_quality_score": float(profile.overall_quality_score),
                        "total_rows": profile.total_rows,
                        "total_columns": profile.total_columns,
                        "duplicate_rows_count": profile.duplicate_rows_count,
                        "missing_cells_count": profile.total_missing_cells,
                    },
                    description=f"Dataset contains {profile.total_rows} rows and {profile.total_columns} columns with an overall data quality score of {profile.overall_quality_score:.1f}/100.",
                    strength_metadata={"importance": 0.6},
                )
            )

        # High missingness columns
        for col_name, col_prof in profile.columns_profile.items():
            missing_pct = (col_prof.null_count / max(1, profile.total_rows)) * 100
            if missing_pct >= 20.0:
                items.append(
                    EvidenceItem(
                        evidence_id=next_id_fn(),
                        source_phase="PHASE3_PROFILE",
                        source_type="DATA_QUALITY",
                        source_id=str(profile.id),
                        columns=[col_name],
                        metrics={
                            "column_name": col_name,
                            "missing_count": col_prof.null_count,
                            "missing_percentage": round(missing_pct, 2),
                        },
                        description=f"Column '{col_name}' has high missingness ({missing_pct:.1f}% missing values).",
                        strength_metadata={"importance": 0.7},
                    )
                )

        return items

    async def _collect_phase5_evidence(
        self, processed_dataset_id: UUID, checksum: str, next_id_fn: Any
    ) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        # Get latest completed visualization run
        stmt = (
            select(VisualizationRun)
            .where(
                VisualizationRun.processed_dataset_id == processed_dataset_id,
                VisualizationRun.status == "COMPLETED",
            )
            .order_by(VisualizationRun.created_at.desc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        run = res.scalar_one_or_none()
        if not run:
            return items

        if run.processed_checksum and run.processed_checksum != checksum:
            logger.warning("Visualization run checksum mismatch with processed dataset.")

        stmt_recs = (
            select(VisualizationRecommendation)
            .where(VisualizationRecommendation.run_id == run.id)
            .order_by(VisualizationRecommendation.score.desc())
            .limit(10)
        )
        res_recs = await self.db.execute(stmt_recs)
        recs = res_recs.scalars().all()

        for rec in recs:
            items.append(
                EvidenceItem(
                    evidence_id=next_id_fn(),
                    source_phase="PHASE5_VISUALIZATION",
                    source_type="VISUALIZATION",
                    source_id=str(rec.id),
                    columns=rec.columns,
                    metrics={
                        "chart_type": rec.chart_type,
                        "relevance_score": rec.score,
                        "reasoning": rec.reasoning,
                    },
                    description=f"Recommended visualization: {rec.chart_type.upper()} chart for {', '.join(rec.columns)} (Relevance score: {rec.score:.1f}/100).",
                    strength_metadata={"score": rec.score},
                )
            )

        return items

    async def _collect_phase6_evidence(
        self, processed_dataset_id: UUID, checksum: str, next_id_fn: Any
    ) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        stmt = (
            select(PatternDiscoveryRun)
            .where(
                PatternDiscoveryRun.processed_dataset_id == processed_dataset_id,
                PatternDiscoveryRun.status == "COMPLETED",
            )
            .order_by(PatternDiscoveryRun.created_at.desc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        run = res.scalar_one_or_none()
        if not run:
            return items

        if run.processed_checksum and run.processed_checksum != checksum:
            logger.warning("Pattern run checksum mismatch with processed dataset.")

        stmt_patterns = (
            select(PatternResult)
            .where(PatternResult.run_id == run.id)
            .order_by(PatternResult.score.desc())
            .limit(20)
        )
        res_patterns = await self.db.execute(stmt_patterns)
        patterns = res_patterns.scalars().all()

        for pat in patterns:
            ptype = pat.pattern_type
            stats = pat.statistics or {}
            items.append(
                EvidenceItem(
                    evidence_id=next_id_fn(),
                    source_phase="PHASE6_PATTERN",
                    source_type=ptype,
                    source_id=str(pat.id),
                    columns=pat.columns,
                    metrics={
                        "score": pat.score,
                        "statistics": stats,
                    },
                    description=f"Pattern detected ({ptype}): {pat.summary} (Score: {pat.score:.1f}/100).",
                    strength_metadata={"score": pat.score, "pattern_type": ptype},
                )
            )

        return items

    async def _collect_phase7_anomaly_evidence(
        self, processed_dataset_id: UUID, checksum: str, next_id_fn: Any
    ) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        stmt = (
            select(AnomalyDetectionRun)
            .where(
                AnomalyDetectionRun.processed_dataset_id == processed_dataset_id,
                AnomalyDetectionRun.status == "COMPLETED",
            )
            .order_by(AnomalyDetectionRun.created_at.desc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        run = res.scalar_one_or_none()
        if not run:
            return items

        if run.processed_checksum and run.processed_checksum != checksum:
            logger.warning("Anomaly run checksum mismatch with processed dataset.")

        # Summary evidence of overall anomalies
        items.append(
            EvidenceItem(
                evidence_id=next_id_fn(),
                source_phase="PHASE7_ANOMALY",
                source_type="ANOMALY_SUMMARY",
                source_id=str(run.id),
                columns=[],
                metrics={
                    "total_observations": run.total_observations,
                    "anomaly_count": run.anomaly_count,
                    "anomaly_percentage": run.anomaly_percentage,
                },
                description=f"Anomaly Detection engine found {run.anomaly_count} anomalous observations ({run.anomaly_percentage:.2f}% of total {run.total_observations} rows).",
                strength_metadata={"anomaly_percentage": run.anomaly_percentage},
            )
        )

        # High/Medium severity anomaly instances
        stmt_anom = (
            select(AnomalyResult)
            .where(
                AnomalyResult.run_id == run.id,
                AnomalyResult.severity.in_(["HIGH", "MEDIUM"]),
            )
            .order_by(AnomalyResult.anomaly_score.desc())
            .limit(15)
        )
        res_anom = await self.db.execute(stmt_anom)
        anomalies = res_anom.scalars().all()

        for anom in anomalies:
            items.append(
                EvidenceItem(
                    evidence_id=next_id_fn(),
                    source_phase="PHASE7_ANOMALY",
                    source_type="ANOMALY",
                    source_id=str(anom.id),
                    columns=[anom.column_name],
                    metrics={
                        "observation_reference": anom.observation_reference,
                        "column_name": anom.column_name,
                        "anomaly_score": anom.anomaly_score,
                        "severity": anom.severity,
                        "methods_detected": anom.methods_detected,
                        "evidence": anom.evidence,
                    },
                    description=f"{anom.severity} anomaly detected in '{anom.column_name}' (obs ref={anom.observation_reference}, score={anom.anomaly_score:.1f}/100, methods={anom.methods_detected}).",
                    strength_metadata={"anomaly_score": anom.anomaly_score, "severity": anom.severity},
                )
            )

        return items

    async def _collect_phase7_prediction_evidence(
        self, processed_dataset_id: UUID, checksum: str, next_id_fn: Any
    ) -> List[EvidenceItem]:
        items: List[EvidenceItem] = []

        stmt = (
            select(PredictionRun)
            .where(
                PredictionRun.processed_dataset_id == processed_dataset_id,
                PredictionRun.status == "COMPLETED",
            )
            .order_by(PredictionRun.created_at.desc())
            .limit(10)
        )
        res = await self.db.execute(stmt)
        runs = res.scalars().all()

        for run in runs:
            if run.processed_checksum and run.processed_checksum != checksum:
                logger.warning("Prediction run checksum mismatch with processed dataset.")

            target = run.target_column
            ptype = run.problem_type
            model = run.model_name
            metrics = run.metrics or {}
            baseline = run.baseline_metrics or {}

            metric_str = ", ".join(f"{k}={v:.4f}" for k, v in metrics.items() if isinstance(v, (int, float)))

            items.append(
                EvidenceItem(
                    evidence_id=next_id_fn(),
                    source_phase="PHASE7_PREDICTION",
                    source_type="PREDICTION",
                    source_id=str(run.id),
                    columns=[target] + (run.feature_columns or []),
                    metrics={
                        "target_column": target,
                        "problem_type": ptype,
                        "model_name": model,
                        "metrics": metrics,
                        "baseline_metrics": baseline,
                        "feature_columns": run.feature_columns,
                        "train_rows": run.training_rows,
                        "test_rows": run.test_rows,
                    },
                    description=f"Prediction model ({model} for target '{target}', {ptype}) achieved test performance: {metric_str} evaluated on {run.test_rows} held-out test rows.",
                    strength_metadata={"problem_type": ptype, "target": target},
                )
            )

        return items
