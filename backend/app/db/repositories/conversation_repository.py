import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.conversation import Conversation
from app.db.models.conversation_message import ConversationMessage


class ConversationRepository:
    """Async repository for Conversation and ConversationMessage entities."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(self, dataset_id: uuid.UUID, title: str = "New Conversation") -> Conversation:
        conversation = Conversation(
            dataset_id=dataset_id,
            title=title,
            status="ACTIVE",
        )
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation_by_id(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_conversations_for_dataset(self, dataset_id: uuid.UUID) -> List[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.dataset_id == dataset_id)
            .order_by(Conversation.updated_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        intent: Optional[str] = None,
        query_plan: Optional[dict] = None,
        query_result_summary: Optional[dict] = None,
        source_references: Optional[list] = None,
        dataset_checksum: Optional[str] = None,
        processed_checksum: Optional[str] = None,
    ) -> ConversationMessage:
        msg = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            intent=intent,
            query_plan=query_plan,
            query_result_summary=query_result_summary,
            source_references=source_references,
            dataset_checksum=dataset_checksum,
            processed_checksum=processed_checksum,
        )
        self.db.add(msg)
        await self.db.flush()
        await self.db.refresh(msg)
        return msg

    async def delete_conversation(self, conversation_id: uuid.UUID) -> bool:
        conv = await self.get_conversation_by_id(conversation_id)
        if conv:
            await self.db.delete(conv)
            await self.db.flush()
            return True
        return False
