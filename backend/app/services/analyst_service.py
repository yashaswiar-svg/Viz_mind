import logging
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.dataset import Dataset
from app.db.models.dataset_profile import DatasetProfile
from app.db.models.conversation import Conversation
from app.db.models.conversation_message import ConversationMessage
from app.db.repositories.conversation_repository import ConversationRepository
from app.services.dataset_loader import DatasetLoader
from app.services.analyst.answer_fallback import AnswerFallback
from app.services.analyst.answer_generator import AnswerGenerator
from app.services.analyst.answer_validator import AnswerValidator
from app.services.analyst.context_resolver import ContextResolver
from app.services.analyst.evidence_builder import EvidenceBuilder
from app.services.analyst.intent_parser import IntentParser
from app.services.analyst.query_executor import QueryExecutor
from app.services.analyst.query_plan import AnalystIntent, QueryPlan
from app.services.analyst.query_planner import QueryPlanner
from app.services.analyst.query_validator import QueryValidator
from app.services.analyst.question_suggester import QuestionSuggester

logger = logging.getLogger(__name__)


class AnalystDatasetVersionMismatchError(Exception):
    """Raised when conversation message dataset_checksum does not match current dataset checksum."""
    pass


class AnalystDatasetNotFoundError(Exception):
    """Raised when requested dataset does not exist."""
    pass


class AnalystService:
    """Main orchestrator for the Phase 9 Natural-Language Data Analyst pipeline."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conv_repo = ConversationRepository(db)
        self.intent_parser = IntentParser()
        self.context_resolver = ContextResolver()
        self.query_planner = QueryPlanner()
        self.query_validator = QueryValidator()
        self.query_executor = QueryExecutor(db)
        self.evidence_builder = EvidenceBuilder()
        self.answer_generator = AnswerGenerator()
        self.answer_validator = AnswerValidator()
        self.answer_fallback = AnswerFallback()
        self.suggester = QuestionSuggester()

    async def _resolve_dataset(self, dataset_id: uuid.UUID) -> Dataset:
        stmt = select(Dataset).where(Dataset.id == dataset_id)
        res = await self.db.execute(stmt)
        dataset = res.scalar_one_or_none()
        if not dataset:
            raise AnalystDatasetNotFoundError(f"Dataset {dataset_id} not found.")
        return dataset

    async def _resolve_profile(self, dataset_id: uuid.UUID) -> List[Dict[str, Any]]:
        stmt = select(DatasetProfile).where(DatasetProfile.dataset_id == dataset_id).order_by(DatasetProfile.created_at.desc())
        res = await self.db.execute(stmt)
        profile = res.scalars().first()
        if not profile or not profile.columns:
            return []
        return profile.columns

    async def process_question(
        self,
        dataset_id: uuid.UUID,
        conversation_id: uuid.UUID,
        user_question: str,
    ) -> ConversationMessage:
        # 1. Resolve dataset and load dataframe + checksum
        dataset = await self._resolve_dataset(dataset_id)
        loader = DatasetLoader(self.db)
        df, current_checksum = await loader.load_dataset(dataset_id)

        # 2. Resolve conversation and verify version integrity before query
        conversation = await self.conv_repo.get_conversation_by_id(conversation_id)
        if not conversation:
            conversation = await self.conv_repo.create_conversation(dataset_id=dataset_id)

        # Version Integrity Check
        if conversation.messages:
            last_msg = conversation.messages[-1]
            if last_msg.dataset_checksum and last_msg.dataset_checksum != current_checksum:
                raise AnalystDatasetVersionMismatchError(
                    f"Dataset version mismatch: conversation was recorded on checksum '{last_msg.dataset_checksum[:8]}' but current dataset is '{current_checksum[:8]}'."
                )

        # 3. Add user message
        await self.conv_repo.add_message(
            conversation_id=conversation.id,
            role="USER",
            content=user_question,
            dataset_checksum=current_checksum,
        )

        # 4. Extract profile metadata
        profile_columns = await self._resolve_profile(dataset_id)

        # 5. Parse Intent
        intent, confidence = self.intent_parser.parse_intent(user_question)

        # 6. Resolve Previous Context if Follow-up
        prev_plan_dict = None
        for m in reversed(conversation.messages):
            if m.role == "ASSISTANT" and m.query_plan:
                prev_plan_dict = m.query_plan
                break

        # 7. Construct QueryPlan
        query_plan = self.query_planner.build_plan(
            intent=intent,
            question=user_question,
            profile_columns=profile_columns,
        )

        # 8. Validate QueryPlan Safety & Bounds
        valid_cols = [c.get("column_name") for c in profile_columns] if profile_columns else list(df.columns)
        self.query_validator.validate_plan(query_plan, valid_columns=valid_cols)

        # 9. Execute QueryPlan (Path A or Path B)
        query_result = await self.query_executor.execute(
            plan=query_plan,
            df=df,
            dataset_id=dataset_id,
            profile_data={"columns": profile_columns},
        )

        # 10. Build Evidence & Answer
        evidence_payload = self.evidence_builder.build_evidence(query_result)

        llm_response = await self.answer_generator.generate_answer(
            question=user_question,
            query_result=query_result,
            evidence_payload=evidence_payload,
        )

        if llm_response:
            final_answer_dict = self.answer_validator.validate_answer(llm_response, query_result)
        else:
            final_answer_dict = self.answer_fallback.generate_fallback(user_question, query_result)

        # Format assistant content string
        content_text = final_answer_dict.get("answer", "")
        if final_answer_dict.get("key_points"):
            content_text += "\n\nKey Findings:\n- " + "\n- ".join(final_answer_dict["key_points"])
        if final_answer_dict.get("limitations"):
            content_text += "\n\nLimitations:\n- " + "\n- ".join(final_answer_dict["limitations"])

        # 11. Persist Assistant Message
        assistant_msg = await self.conv_repo.add_message(
            conversation_id=conversation.id,
            role="ASSISTANT",
            content=content_text,
            intent=intent.value,
            query_plan=query_plan.model_dump(),
            query_result_summary={
                "operation": query_result.operation.value,
                "summary": query_result.summary_text,
                "metrics": query_result.metrics,
                "data": query_result.data[:10],
                "execution_path": query_result.execution_path,
                "source_type": query_result.source_type,
            },
            source_references=evidence_payload.get("source_references"),
            dataset_checksum=current_checksum,
        )

        return assistant_msg

    async def get_suggestions(self, dataset_id: uuid.UUID) -> List[str]:
        profile_columns = await self._resolve_profile(dataset_id)
        return self.suggester.suggest_questions(profile_columns)
