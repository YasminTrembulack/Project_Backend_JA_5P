import logging
import os

import pytest

from app.core.settings import InterceptHandler, Settings


def test_settings(mocker):
    mocker.patch.dict(
        os.environ,
        {
            'DATABASE_URL': 'test_database_url',
            'DATABASE_TYPE': 'test_database_type',
            'SECRET_KEY': 'test_secret_key',
            'ALGORITHM': 'test_algorithm',
        },
    )

    settings = Settings()
    assert settings.DATABASE_URL == 'test_database_url'
    assert settings.DATABASE_TYPE == 'test_database_type'
    assert settings.SECRET_KEY == 'test_secret_key'
    assert settings.ALGORITHM == 'test_algorithm'


@pytest.fixture
def log_handler():
    handler = InterceptHandler()
    logging.getLogger().addHandler(handler)
    yield handler
    logging.getLogger().removeHandler(handler)


def test_intercept_handler(caplog, log_handler):
    with caplog.at_level(logging.INFO):
        logging.getLogger().info('Teste de log interceptado')

    assert 'Teste de log interceptado' in caplog.text
