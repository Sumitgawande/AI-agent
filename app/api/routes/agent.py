from fastapi import APIRouter, Depends, HTTPException, Path

from ...schemas.agent import AgentRunRequest, AgentRunResponse
from ...services.agent_service import get_agent_service

router = APIRouter()


@router.post("/agents/{agent_id}/run", response_model=AgentRunResponse, tags=["agents"])
def run_agent(
    agent_id: str = Path(..., description="Agent identifier"),
    payload: AgentRunRequest | None = None,
    agent_svc=Depends(get_agent_service),
) -> AgentRunResponse:
    # agent_id is reserved for future multi-agent support
    if payload is None:
        raise HTTPException(status_code=400, detail="input required")
    try:
        out = agent_svc.run(payload.input)
    except Exception:
        raise HTTPException(status_code=500, detail="AGENT_EXECUTION_FAILED")

    return AgentRunResponse(output=out)
