import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api.routes import agent, chat, conversation, health
from .core.logging import configure_logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="AI Agent Service")

    app.add_api_route("/api/v1/health", health.health, methods=["GET"])
    app.add_api_route("/api/v1/chat", chat.chat, methods=["POST"])
    app.add_api_route(
        "/api/v1/agents/{agent_id}/run",
        agent.run_agent,
        methods=["POST"],
    )
    app.add_api_route("/api/v1/sessions", conversation.create_session, methods=["POST"])
    app.add_api_route("/api/v1/sessions/{session_id}", conversation.get_session, methods=["GET"])
    app.add_api_route("/api/v1/sessions", conversation.list_sessions, methods=["GET"])
    app.add_api_route("/api/v1/sessions/{session_id}", conversation.delete_session, methods=["DELETE"])
    app.add_api_route(
        "/api/v1/sessions/{session_id}/messages",
        conversation.add_message,
        methods=["POST"],
    )
    app.add_api_route(
        "/api/v1/sessions/{session_id}/messages",
        conversation.list_messages,
        methods=["GET"],
    )

    @app.exception_handler(Exception)
    async def _global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Unable to complete the request.",
                }
            },
        )

    return app


app = create_app()
