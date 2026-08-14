from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel


class SessionCreateRequest(BaseModel):
    metadata: Dict[str, Any] | None = None
    user_id: int | None = None


class SessionResponse(BaseModel):
    id: str
    user_id: int | None = None
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    summary: str
    summary_updated_at: datetime | None = None

    class Config:
        orm_mode = True


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]


class MessageCreateRequest(BaseModel):
    role: str
    content: str
    metadata: Dict[str, Any] | None = None


class MessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True
