from fastapi import APIRouter

from .routes import agent, chat, conversation, health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(agent.router)
api_router.include_router(conversation.router)
