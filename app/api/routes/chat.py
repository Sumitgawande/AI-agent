from fastapi import APIRouter, Depends, HTTPException

from ...schemas.chat import ChatRequest, ChatResponse
from ...services.agent_service import get_agent_service
from ...services.conversation_service import ConversationService, get_conversation_service
from ...services.context_builder import ContextBuilder

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
def chat(
    payload: ChatRequest,
    agent_svc=Depends(get_agent_service),
    conversation_svc=Depends(get_conversation_service),
) -> ChatResponse:
    session = None
    if payload.session_id:
        session = conversation_svc.get_session(payload.session_id)
        if session is None:
            session = conversation_svc.create_session(session_id=payload.session_id)
    else:
        session = conversation_svc.create_session()

    conversation_svc.add_message(session.id, role="user", content=payload.message)

    try:
        if getattr(agent_svc._agent, "provider", "local") == "local":
            result = agent_svc.run(payload.message, session.id)
        else:
            builder = ContextBuilder(conversation_svc)
            context = builder.build_context(session.id, payload.message)["context"]
            result = agent_svc.run(payload.message, session.id, context=context)
    except Exception:
        raise HTTPException(status_code=500, detail="AGENT_EXECUTION_FAILED")

    conversation_svc.add_message(session.id, role="assistant", content=result)
    return ChatResponse(response=result, session_id=session.id)
