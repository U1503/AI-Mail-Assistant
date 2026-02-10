# backend/app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

# ------------------------------------------------------------------
# Database URL
# ------------------------------------------------------------------
# Priority:
# 1. DATABASE_URL from env (Postgres in prod)
# 2. SQLite fallback for local development
# ------------------------------------------------------------------

DATABASE_URL = settings.DATABASE_URL or "sqlite:///./email_assistant.db"
# print("DB URL:", DATABASE_URL)    #python -m app.core.database

# SQLite needs special flag
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# ------------------------------------------------------------------
# SQLAlchemy Engine & Session
# ------------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False,               # set True for SQL debugging
    future=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ------------------------------------------------------------------
# Base class for ORM models
# ------------------------------------------------------------------

Base = declarative_base()


# ------------------------------------------------------------------
# DB initialization (auto-create schema)
# ------------------------------------------------------------------

def init_db():
    """
    Initialize database and create tables automatically.
    This should be called once at application startup.
    """
    from app.models import db_models  # noqa: F401 (import registers models)
    Base.metadata.create_all(bind=engine)


# ------------------------------------------------------------------
# Dependency helper (optional, future use)
# ------------------------------------------------------------------

def get_db():
    """
    Yields a database session.
    Useful for FastAPI dependencies later.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



