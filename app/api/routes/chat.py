from fastapi import APIRouter, Depends, HTTPException

from ...schemas.chat import ChatRequest, ChatResponse
from ...services.agent_service import get_agent_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
def chat(
    payload: ChatRequest,
    agent_svc=Depends(get_agent_service),
) -> ChatResponse:
    try:
        result = agent_svc.run(payload.message, payload.session_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="AGENT_EXECUTION_FAILED")

    return ChatResponse(response=result, session_id=payload.session_id)
