import os

from app.core.settings import Settings


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
