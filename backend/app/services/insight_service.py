import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.models.dataset import Dataset
from app.db.models.dataset_profile import DatasetProfile
from app.db.models.insight_run import InsightRun
from app.db.models.insight import Insight
from app.db.repositories.insight_repository import InsightRepository
from app.services.insight_evidence_service import InsightEvidenceService, InsightVersionMismatchError
from app.services.insight_candidate_generator import InsightCandidateGenerator, InsightCandidate
from app.services.insight_scoring import InsightScoringEngine
from app.services.insight_prompt_builder import InsightPromptBuilder
from app.services.insight_validator import InsightValidator, InsightValidationError
from app.services.insight_fallback import InsightFallbackEngine
from app.services.insight_deduplication import InsightDeduplicationEngine
from app.services.llm.provider_factory import get_llm_provider
from app.services.llm.base_provider import LLMProviderError

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class NoEvidenceError(Exception):
    """Raised when no Phase 3-7 analytical evidence is available for a dataset."""
    pass


class PreprocessingRequiredError(Exception):
    """Raised when dataset has not been preprocessed."""
    pass


class InsightService:
    """Main orchestrator for the Phase 8 AI Insight Engine pipeline."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = InsightRepository(db)
        self.evidence_service = InsightEvidenceService(db)
        self.candidate_generator = InsightCandidateGenerator()
        self.scoring_engine = InsightScoringEngine()
        self.prompt_builder = InsightPromptBuilder()
        self.validator = InsightValidator()
        self.fallback_engine = InsightFallbackEngine()
        self.dedup_engine = InsightDeduplicationEngine()

    async def generate_insights(self, dataset_id: UUID) -> Tuple[InsightRun, List[Insight]]:
        """
        Executes complete end-to-end insight generation pipeline.
        """
        # 1. Resolve source and processed datasets
        dataset = await self._resolve_dataset(dataset_id)

        # 2. Resolve processed dataset
        processed_dataset = await self._resolve_processed_dataset(dataset)
        if not processed_dataset:
            raise PreprocessingRequiredError(f"Dataset {dataset_id} requires preprocessing prior to insight generation.")

        # 3. Resolve profile
        profile = await self._resolve_profile(dataset.id)
        if not profile:
            raise PreprocessingRequiredError(f"Dataset profile missing for dataset {dataset_id}.")

        # 4. Create InsightRun
        run = InsightRun(
            dataset_id=dataset.id,
            processed_dataset_id=processed_dataset.id,
            profile_id=profile.id,
            processed_checksum=processed_dataset.processed_checksum,
            status="RUNNING",
            provider=settings.LLM_PROVIDER if settings.LLM_ENABLED else "mock",
            model=settings.LLM_MODEL if settings.LLM_ENABLED else "deterministic_fallback",
            started_at=utc_now(),
        )
        await self.repo.create_run(run)

        try:
            # 5. Collect Evidence
            evidence_items, checksum = await self.evidence_service.collect_evidence(
                dataset=dataset,
                processed_dataset=processed_dataset,
                profile=profile,
            )
            run.evidence_count = len(evidence_items)

            if not evidence_items:
                run.status = "COMPLETED"
                run.completed_at = utc_now()
                run.error_message = "No analytical evidence items were found for this dataset."
                await self.repo.update_run(run)
                return run, []

            # 6. Generate Candidates
            candidates = self.candidate_generator.generate_candidates(evidence_items)
            run.candidate_count = len(candidates)

            if not candidates:
                run.status = "COMPLETED"
                run.completed_at = utc_now()
                run.error_message = "No insight candidates could be generated from available evidence."
                await self.repo.update_run(run)
                return run, []

            # 7. LLM Provider setup
            provider = get_llm_provider(settings.LLM_PROVIDER)
            sys_inst = self.prompt_builder.build_system_instruction()

            processed_insights: List[Dict[str, Any]] = []
            any_fallback_used = False

            for cand in candidates:
                fallback_needed = False
                llm_output = None
                gen_mode = "LLM"

                if settings.LLM_ENABLED and settings.LLM_PROVIDER != "mock":
                    try:
                        prompt, schema = self.prompt_builder.build_user_prompt(cand)
                        raw_completion = await provider.generate_completion(prompt, sys_inst, schema)
                        self.validator.validate_llm_output(
                            output=raw_completion,
                            candidate_evidence_ids=cand.evidence_ids,
                            insight_type=cand.insight_type,
                        )
                        llm_output = raw_completion
                        gen_mode = "LLM"
                    except (LLMProviderError, InsightValidationError, Exception) as err:
                        logger.warning(
                            f"LLM generation/validation failed for candidate {cand.candidate_id} ({err}). Switching to fallback."
                        )
                        fallback_needed = True

                if not settings.LLM_ENABLED or settings.LLM_PROVIDER == "mock" or fallback_needed:
                    llm_output = self.fallback_engine.generate_fallback_insight(cand)
                    gen_mode = "DETERMINISTIC_FALLBACK"
                    any_fallback_used = True

                # Compute Score & Importance & Evidence Strength
                score, imp_level, ev_strength = self.scoring_engine.compute_candidate_score(
                    insight_type=cand.insight_type,
                    evidence_items=cand.evidence_items,
                )

                insight_dict = {
                    "insight_type": cand.insight_type,
                    "title": llm_output.get("title", cand.title_template),
                    "summary": llm_output.get("summary", ""),
                    "explanation": llm_output.get("explanation", ""),
                    "importance_score": score,
                    "importance_level": imp_level,
                    "evidence_strength": ev_strength,
                    "columns": cand.target_columns,
                    "statistics": cand.candidate_metrics,
                    "limitations": llm_output.get("limitations", []),
                    "generation_mode": gen_mode,
                    "validation_status": "VALIDATED",
                    "evidence_items": [e.to_dict() for e in cand.evidence_items],
                }

                processed_insights.append(insight_dict)

            # 8. Deduplicate
            deduped_insights = self.dedup_engine.deduplicate_insights(processed_insights)

            # 9. Rank & Limit
            final_insights_data = sorted(
                deduped_insights,
                key=lambda x: x["importance_score"],
                reverse=True,
            )[: settings.MAX_INSIGHTS_PER_RUN]

            # 10. Persist
            saved_insights = await self.repo.save_insights_and_evidence(
                run_id=run.id,
                dataset_id=dataset.id,
                processed_dataset_id=processed_dataset.id,
                insights_data=final_insights_data,
            )

            # 11. Complete Run
            run.fallback_used = any_fallback_used
            run.insight_count = len(saved_insights)
            run.status = "COMPLETED_WITH_FALLBACK" if any_fallback_used else "COMPLETED"
            run.completed_at = utc_now()
            await self.repo.update_run(run)

            return run, saved_insights

        except Exception as e:
            logger.error(f"Insight service run failed: {e}", exc_info=True)
            run.status = "FAILED"
            run.completed_at = utc_now()
            run.error_message = str(e)
            await self.repo.update_run(run)
            raise e

    async def _resolve_dataset(self, dataset_id: UUID) -> Dataset:
        stmt = select(Dataset).where(Dataset.id == dataset_id)
        res = await self.db.execute(stmt)
        ds = res.scalar_one_or_none()
        if not ds:
            raise ValueError(f"Dataset {dataset_id} not found.")
        return ds

    async def _resolve_processed_dataset(self, dataset: Dataset) -> Optional[Dataset]:
        if dataset.dataset_kind == "PROCESSED":
            return dataset

        stmt = (
            select(Dataset)
            .where(
                Dataset.parent_dataset_id == dataset.id,
                Dataset.dataset_kind == "PROCESSED",
            )
            .order_by(Dataset.created_at.desc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def _resolve_profile(self, dataset_id: UUID) -> Optional[DatasetProfile]:
        stmt = (
            select(DatasetProfile)
            .where(DatasetProfile.dataset_id == dataset_id)
            .order_by(DatasetProfile.created_at.desc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
