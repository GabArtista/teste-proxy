from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings

engine = create_engine(settings.db_url(), pool_pre_ping=True, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, future=True)


def get_session():
    """FastAPI dependency-style session generator."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
