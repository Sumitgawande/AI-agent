from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path

from ...schemas.conversation import (
    MessageCreateRequest,
    MessageResponse,
    SessionCreateRequest,
    SessionListResponse,
    SessionResponse,
)
from ...services.conversation_service import ConversationService, get_conversation_service

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse, tags=["sessions"])
def create_session(
    payload: SessionCreateRequest,
    svc=Depends(get_conversation_service),
) -> SessionResponse:
    try:
        session = svc.create_session(metadata=payload.metadata, user_id=payload.user_id)
    except Exception:
        raise HTTPException(status_code=500, detail="SESSION_CREATION_FAILED")
    return session


@router.get("/sessions/{session_id}", response_model=SessionResponse, tags=["sessions"])
def get_session(
    session_id: str = Path(..., description="Session identifier"),
    svc=Depends(get_conversation_service),
) -> SessionResponse:
    session = svc.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    return session


@router.get("/sessions", response_model=SessionListResponse, tags=["sessions"])
def list_sessions(
    limit: int = 100,
    offset: int = 0,
    svc=Depends(get_conversation_service),
) -> SessionListResponse:
    sessions = svc.list_sessions(limit=limit, offset=offset)
    return SessionListResponse(sessions=sessions)


@router.delete("/sessions/{session_id}", tags=["sessions"])
def delete_session(
    session_id: str = Path(..., description="Session identifier"),
    svc=Depends(get_conversation_service),
) -> dict:
    try:
        svc.delete_session(session_id)
    except Exception:
        raise HTTPException(status_code=500, detail="SESSION_DELETION_FAILED")
    return {"deleted": True}


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse, tags=["sessions"])
def add_message(
    session_id: str = Path(..., description="Session identifier"),
    payload: MessageCreateRequest = None,
    svc=Depends(get_conversation_service),
) -> MessageResponse:
    if payload is None:
        raise HTTPException(status_code=400, detail="input required")
    try:
        message = svc.add_message(
            session_id=session_id,
            role=payload.role,
            content=payload.content,
            metadata=payload.metadata,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    except Exception:
        raise HTTPException(status_code=500, detail="MESSAGE_CREATION_FAILED")
    return message


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse], tags=["sessions"])
def list_messages(
    session_id: str = Path(..., description="Session identifier"),
    limit: int = 100,
    offset: int = 0,
    svc=Depends(get_conversation_service),
) -> List[MessageResponse]:
    if svc.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    messages = svc.get_messages(session_id=session_id, limit=limit, offset=offset)
    return messages
