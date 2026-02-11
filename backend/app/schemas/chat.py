from pydantic import BaseModel
from datetime import datetime
from typing import List


class ChatRequest(BaseModel):
    """Chat request schema."""
    
    document_id: int
    question: str
    session_id: int | None = None


class ChatResponse(BaseModel):
    """Chat response schema."""
    
    answer: str
    session_id: int
    sources: List[str] = []


class ChatMessageSchema(BaseModel):
    """Chat message schema."""
    
    role: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    """Chat history response schema."""
    
    session_id: int
    document_id: int
    messages: List[ChatMessageSchema]
