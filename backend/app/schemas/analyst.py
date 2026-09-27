import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ConversationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: Optional[str] = Field(default="New Conversation")


class MessageSendRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    content: str = Field(..., min_length=1, description="Natural language question")


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    intent: Optional[str] = None
    query_plan: Optional[Dict[str, Any]] = None
    query_result_summary: Optional[Dict[str, Any]] = None
    source_references: Optional[List[Dict[str, Any]]] = None
    dataset_checksum: Optional[str] = None
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    title: str
    status: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = Field(default_factory=list)


class SuggestionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    suggestions: List[str]
