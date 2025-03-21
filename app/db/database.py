from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.settings import Settings

engine = create_engine(Settings().DATABASE_URL)

try:
    with engine.connect() as connection:
        logger.info(
            f"Successfully connected to {Settings().DATABASE_TYPE} database."
        )
except Exception as e:
    logger.error(f"Failed to connect to the database: {e}")


def get_session():
    with Session(engine) as session:
        yield session
