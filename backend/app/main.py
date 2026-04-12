from fastapi import FastAPI
import uvicorn

from app.core.config import get_settings
from app.db.init_db import init_db
from app.middleware.auth import AuthMiddleware
from app.routers.router import api_router


settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.add_middleware(AuthMiddleware)

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    app.include_router(api_router)
    return app


app = create_app()


def run() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.is_development,
    )
