import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api.router import api_router
from .core.logging import configure_logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="AI Agent Service")
    app.include_router(api_router)

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
