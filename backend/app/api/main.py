from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.api.v1 import legal
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.database import init_db
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="DClaw Legal",
        description="AI contract review API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(",") if hasattr(settings, "cors_origins") else ["http://localhost:3013"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(legal.router, prefix="/api/v1", tags=["legal"])

    return app


app = create_app()
