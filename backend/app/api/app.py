from __future__ import annotations

from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from backend.app.api.dependencies import ApplicationContainer
from backend.app.api.routes import classifications_router, decisions_router
from backend.app.core.errors import ConfigurationError, EntityNotFoundError
from backend.app.infrastructure.persistence.repositories import (
    PersistenceConflictError,
    PersistenceInvariantError,
)


ShutdownCallback = Callable[[], Awaitable[None]]


def create_app(
    container: ApplicationContainer,
    shutdown_callbacks: tuple[ShutdownCallback, ...] = (),
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
        yield
        for callback in shutdown_callbacks:
            await callback()

    application = FastAPI(
        title="AI Classifier Agent API",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.state.container = container
    application.include_router(classifications_router)
    application.include_router(decisions_router)

    async def health() -> dict[str, str]:
        return {"status": "ok"}

    async def entity_not_found_handler(
        request: Request,
        error: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(error)},
        )

    async def configuration_error_handler(
        request: Request,
        error: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(error)},
        )

    async def persistence_conflict_handler(
        request: Request,
        error: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )

    async def persistence_invariant_handler(
        request: Request,
        error: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(error)},
        )

    application.add_api_route("/health", health, methods=["GET"])
    application.add_exception_handler(EntityNotFoundError, entity_not_found_handler)
    application.add_exception_handler(ConfigurationError, configuration_error_handler)
    application.add_exception_handler(PersistenceConflictError, persistence_conflict_handler)
    application.add_exception_handler(PersistenceInvariantError, persistence_invariant_handler)

    return application
