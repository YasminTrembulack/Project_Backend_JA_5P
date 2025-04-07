from unittest.mock import ANY, MagicMock, patch

import pytest

from app.db import database
from app.types.exceptions import DatabaseConnectionError, MigrationExecutionError


def test_connection_success():
    with patch('app.db.database.engine.connect') as mock_connect:
        mock_connect.return_value.__enter__.return_value = MagicMock()

        database.test_connection()

        mock_connect.assert_called()


def test_connection_failure():
    with patch('app.db.database.engine.connect', side_effect=Exception('fail')):
        with pytest.raises(DatabaseConnectionError):
            database.test_connection()


def test_run_migrations_success():
    with patch('app.db.database.engine.connect') as mock_connect, \
         patch('alembic.command.upgrade') as mock_upgrade:
        mock_connect.return_value = MagicMock()
        mock_upgrade.return_value = None

        database.run_migrations()

        mock_connect.assert_called_once()
        mock_upgrade.assert_called_once_with(ANY, 'head')


def test_run_migrations_failure():
    with patch('app.db.database.engine.connect') as mock_connect, \
         patch('alembic.command.upgrade', side_effect=Exception()):

        mock_connect.return_value = MagicMock()

        with pytest.raises(
            MigrationExecutionError,
            match='An error occurred while executing database migrations.'
        ):
            database.run_migrations()


def test_get_session_yields_session():
    mock_session = MagicMock()
    with patch('app.db.database.import_models') as mock_import_models, \
         patch('app.db.database.SessionLocal') as mock_session_local:

        mock_session_local.return_value.__enter__.return_value = mock_session

        session_gen = database.get_session()
        result = next(session_gen)

        assert result == mock_session

        mock_import_models.assert_called_once()
