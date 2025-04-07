from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from app.middlewares.authentication import AuthenticationMiddleware


@pytest.fixture
def client():
    app = FastAPI()
    app.add_middleware(AuthenticationMiddleware)

    @app.get('/api/login')
    async def login_endpoint():
        return JSONResponse(status_code=200, content={'message': 'No auth required'})

    @app.get('/api/protected')
    async def protected_endpoint(request: Request):
        return JSONResponse(status_code=200, content={'message': 'Authorized'})

    return TestClient(app)


def test_missing_token_returns_401(client):
    response = client.get('/api/protected')
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == 'Authentication token is missing'


@patch('app.middlewares.authentication.security.verify_access_token')
def test_invalid_token_returns_401(mock_verify, client):
    mock_verify.side_effect = Exception('Token inválido')

    headers = {'Authorization': 'Bearer invalidtoken'}
    response = client.get('/api/protected', headers=headers)

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert 'Unexpected error' in response.json()['detail']


@patch('app.middlewares.authentication.security.verify_access_token')
@patch('app.middlewares.authentication.get_session')
@patch('app.middlewares.authentication.UserRepository')
def test_user_not_found_returns_401(
    mock_repo, mock_get_session, mock_verify, client
):
    mock_verify.return_value = {'user_id': '123'}

    mock_session = MagicMock()
    mock_session.close = MagicMock()
    mock_get_session.return_value = iter([mock_session])

    repo_instance = MagicMock()
    repo_instance.get_user_by_field.return_value = None
    mock_repo.return_value = repo_instance

    headers = {'Authorization': 'Bearer validtoken'}
    response = client.get('/api/protected', headers=headers)

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert 'Invalid token' in response.text


@patch('app.middlewares.authentication.security.verify_access_token')
@patch('app.middlewares.authentication.get_session')
@patch('app.middlewares.authentication.UserRepository')
def test_valid_token_and_user_passes_middleware(
    mock_repo, mock_get_session, mock_verify, client
):
    mock_verify.return_value = {'user_id': '123'}

    mock_session = MagicMock()
    mock_session.close = MagicMock()
    mock_get_session.return_value = iter([mock_session])

    repo_instance = MagicMock()
    repo_instance.get_user_by_field.return_value = {'id': '123'}
    mock_repo.return_value = repo_instance

    headers = {'Authorization': 'Bearer validtoken'}
    response = client.get('/api/protected', headers=headers)

    assert response.status_code == HTTP_200_OK
    assert response.json()['message'] == 'Authorized'


def test_login_route_skips_authentication(client):
    response = client.get('/api/login')
    assert response.status_code == HTTP_200_OK
    assert response.json()['message'] == 'No auth required'
