import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_dataset_ownership
from app.db.database import get_db
from app.schemas.analyst import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageResponse,
    MessageSendRequest,
    SuggestionResponse,
)
from app.services.analyst_service import (
    AnalystDatasetNotFoundError,
    AnalystDatasetVersionMismatchError,
    AnalystService,
)

router = APIRouter(prefix="/datasets/{dataset_id}/analyst", tags=["analyst"])


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    dataset_id: uuid.UUID,
    payload: ConversationCreateRequest = ConversationCreateRequest(),
    dataset=Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    service = AnalystService(db)
    try:
        await service._resolve_dataset(dataset_id)
        conv = await service.conv_repo.create_conversation(dataset_id=dataset_id, title=payload.title or "New Conversation")
        conv_full = await service.conv_repo.get_conversation_by_id(conv.id)
        return conv_full
    except AnalystDatasetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    dataset_id: uuid.UUID,
    dataset=Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    service = AnalystService(db)
    convs = await service.conv_repo.get_conversations_for_dataset(dataset_id)
    return convs


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    dataset_id: uuid.UUID,
    conversation_id: uuid.UUID,
    dataset=Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    service = AnalystService(db)
    conv = await service.conv_repo.get_conversation_by_id(conversation_id)
    if not conv or conv.dataset_id != dataset_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return conv


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    dataset_id: uuid.UUID,
    conversation_id: uuid.UUID,
    payload: MessageSendRequest,
    dataset=Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    service = AnalystService(db)
    try:
        assistant_msg = await service.process_question(
            dataset_id=dataset_id,
            conversation_id=conversation_id,
            user_question=payload.content,
        )
        await db.commit()
        return assistant_msg
    except AnalystDatasetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AnalystDatasetVersionMismatchError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "ANALYST_DATASET_VERSION_MISMATCH", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    dataset_id: uuid.UUID,
    conversation_id: uuid.UUID,
    dataset=Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    service = AnalystService(db)
    success = await service.conv_repo.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    await db.commit()
    return None


@router.get("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    dataset_id: uuid.UUID,
    dataset=Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    service = AnalystService(db)
    try:
        suggestions = await service.get_suggestions(dataset_id)
        return SuggestionResponse(suggestions=suggestions)
    except AnalystDatasetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

