"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lagos_fare.config import get_settings
from lagos_fare.dependencies import init_fare_model
from lagos_fare.infrastructure.db.database import init_db
from lagos_fare.presentation.api.errors import register_exception_handlers
from lagos_fare.presentation.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_db()
    init_fare_model(settings)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Lagos Transport Fare Prediction — ML, routing, weather, and Nigerian pricing engine.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(api_v1_router, prefix="/api/v1")
    return app


app = create_app()
