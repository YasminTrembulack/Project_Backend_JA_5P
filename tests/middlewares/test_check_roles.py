from unittest.mock import MagicMock

import pytest
from fastapi import Depends, FastAPI, Request, status
from fastapi.testclient import TestClient

from app.middlewares.check_roles import check_roles, get_current_user
from app.models.user import User
from app.types.exceptions import NotAuthenticatedError, PermissionDeniedError

mock_admin_user = User(full_name='Admin User', role='Admin')
mock_regular_user = User(full_name='Regular User', role='User')
mock_editor_user = User(full_name='Editor User', role='Editor')


@pytest.fixture
def client():
    app = FastAPI()

    @app.get('/admin')
    def admin_route(user: User = Depends(check_roles(['Admin']))):
        return {'message': 'Admin route accessed', 'username': user.full_name}

    @app.get('/user')
    def user_route(user: User = Depends(check_roles(['User']))):
        return {'message': 'User route accessed', 'username': user.full_name}

    @app.get('/editor')
    def editor_route(user: User = Depends(check_roles(['Editor']))):
        return {'message': 'Editor route accessed', 'username': user.full_name}

    return TestClient(app)


@pytest.mark.parametrize(
    ('mock_user', 'user_type'),
    [
        (mock_admin_user, 'Admin'),
        (mock_regular_user, 'User'),
        (mock_editor_user, 'Editor'),
    ],
)
def test_check_roles_allowed(mock_user, user_type, client):
    client.app.dependency_overrides[get_current_user] = lambda: mock_user
    response = client.get(f'/{user_type.lower()}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'message': f'{user_type} route accessed',
        'username': f'{user_type if user_type != "User" else "Regular"} User',
    }


@pytest.mark.parametrize(
    ('mock_user', 'user_type'),
    [
        (mock_admin_user, 'Admin'),
        (mock_regular_user, 'User'),
        (mock_editor_user, 'Editor'),
    ],
)
def test_check_roles_denied(mock_user, user_type, client):
    client.app.dependency_overrides[get_current_user] = lambda: mock_user
    route = 'admin' if user_type != 'Admin' else 'user'
    with pytest.raises(
        PermissionDeniedError,
        match=f'Permission denied, only {route.capitalize()} allowed.',
    ):
        client.get(f'/{route}', headers={'X-Username': 'user'})


def test_get_current_user_authenticated():
    mock_request = MagicMock(spec=Request)
    mock_request.state.user = mock_admin_user

    user = get_current_user(mock_request)
    assert user.full_name == 'Admin User'
    assert user.role == 'Admin'


def test_get_current_user_no_user():
    mock_request = MagicMock(spec=Request)
    del mock_request.state.user

    with pytest.raises(NotAuthenticatedError, match='Not authenticated'):
        get_current_user(mock_request)


def test_get_current_user_none():
    mock_request = MagicMock(spec=Request)
    mock_request.state.user = None

    with pytest.raises(NotAuthenticatedError, match='Not authenticated'):
        get_current_user(mock_request)
