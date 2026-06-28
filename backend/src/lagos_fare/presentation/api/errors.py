"""Global exception handlers — RFC 7807-inspired JSON errors."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from lagos_fare.application.exceptions import ExternalServiceError, ModelNotLoadedError, NotFoundError
from lagos_fare.domain.exceptions import DomainError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "type": exc.code,
                "title": "Domain error",
                "status": 400,
                "detail": exc.message,
            },
        )

    @app.exception_handler(ExternalServiceError)
    async def external_error_handler(_request: Request, exc: ExternalServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={
                "type": "external_service_error",
                "title": "External service error",
                "status": 502,
                "detail": exc.message,
                "service": exc.service,
            },
        )

    @app.exception_handler(ModelNotLoadedError)
    async def model_error_handler(_request: Request, exc: ModelNotLoadedError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "type": "service_unavailable",
                "title": "Model unavailable",
                "status": 503,
                "detail": exc.message,
            },
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "type": "not_found",
                "title": "Not found",
                "status": 404,
                "detail": exc.message,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [
            {"field": ".".join(str(x) for x in err["loc"]), "message": err["msg"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "type": "validation_error",
                "title": "Invalid request",
                "status": 422,
                "detail": "Request validation failed",
                "errors": errors,
            },
        )

    @app.exception_handler(Exception)
    async def generic_handler(_request: Request, exc: Exception) -> JSONResponse:
        from lagos_fare.config import get_settings

        detail = str(exc) if get_settings().debug else "An unexpected error occurred."
        return JSONResponse(
            status_code=500,
            content={
                "type": "internal_error",
                "title": "Internal server error",
                "status": 500,
                "detail": detail,
            },
        )
