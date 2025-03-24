import logging
import sys

from dotenv import load_dotenv
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    DATABASE_URL: str
    DATABASE_TYPE: str
    SECRET_KEY: str
    ALGORITHM: str
    LOCAL_ENV: bool = False
    VERSION: str = '0.1.0'
    API_PREFIX: str = '/api'
    PROJECT_NAME: str = 'API_JA_5P'


class InterceptHandler(logging.Handler):
    @staticmethod
    def emit(record: logging.LogRecord) -> None:
        logger_opt = logger.opt(depth=7, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


LOGGING_LEVEL = logging.DEBUG if Settings().LOCAL_ENV else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{'sink': sys.stderr, 'level': LOGGING_LEVEL}])
