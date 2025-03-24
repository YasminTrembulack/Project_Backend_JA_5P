from alembic import command
from alembic.config import Config
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import Settings
from app.types.exceptions import DatabaseConnectionError, MigrationExecutionError

engine = create_engine(Settings().DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_connection():
    try:
        with engine.connect():
            logger.info(
                f'Successfully connected to {Settings().DATABASE_TYPE} database.'
            )
    except Exception:
        raise DatabaseConnectionError(
            f'Failed to connect to {Settings().DATABASE_TYPE} database.'
        )
    finally:
        engine.dispose()


def run_migrations():
    try:
        alembic_cfg = Config('alembic.ini')
        with engine.connect() as connection:
            alembic_cfg.attributes['connection'] = connection
            logger.info('Running migrations...')
            command.upgrade(alembic_cfg, 'head')
            logger.info('Migrations executed successfully!')
    except Exception as e:
        logger.error(f'Error during migrations execution: {e}')
        raise MigrationExecutionError(
            'An error occurred while executing database migrations.'
        )
    finally:
        engine.dispose()


def get_session():
    with SessionLocal() as session:
        yield session
