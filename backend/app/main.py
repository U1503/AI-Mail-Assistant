# backend/app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Mail Assistant API starting up...")
    init_db()
    yield
    print("🛑 Mail Assistant API shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Email Assistant",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ✅ Allow ngrok + local frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8501",      # Streamlit local
            "http://127.0.0.1:8501",
            "https://*.ngrok-free.app",   # any ngrok domain
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        chat_router,
        prefix="/api",
        tags=["Email Assistant"],
    )

    return app


app = create_app()
