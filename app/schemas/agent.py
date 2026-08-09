from pydantic import BaseModel


class AgentRunRequest(BaseModel):
    input: str


class AgentRunResponse(BaseModel):
    output: str
