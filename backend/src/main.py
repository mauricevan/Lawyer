"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.src.config import settings
from backend.src.database import engine, init_db
from backend.src.routes import admin, conversations, documents, export, health, query


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="EUR-Lex RAG API",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(query.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
