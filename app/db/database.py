from alembic import command
from alembic.config import Config
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import Settings

engine = create_engine(Settings().DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_connection():
    try:
        with engine.connect():
            logger.info(
                f"Successfully connected to {Settings().DATABASE_TYPE} database."
            )
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        raise e
    finally:
        engine.dispose()


def run_migrations():
    try:
        alembic_cfg = Config("alembic.ini")
        with engine.connect() as connection:
            alembic_cfg.attributes['connection'] = connection
            logger.info("Executando migrations...")
            command.upgrade(alembic_cfg, "head")
            logger.info("Migrations executadas com sucesso!")
    except Exception as e:
        logger.error(f"Error during migrations execution: {e}")
        raise
    finally:
        engine.dispose()


def get_session():
    with SessionLocal() as session:
        yield session
