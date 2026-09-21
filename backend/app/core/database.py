from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine_options = {'pool_pre_ping': True}
if not settings.database_url.startswith('sqlite'):
    engine_options.update({
        'pool_size': settings.database_pool_size,
        'max_overflow': settings.database_max_overflow,
        'pool_timeout': settings.database_pool_timeout_seconds,
        'pool_recycle': settings.database_pool_recycle_seconds,
    })
engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
