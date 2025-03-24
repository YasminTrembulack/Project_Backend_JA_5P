import pytest

from app.core.security import SecurityManager
from app.types.exceptions import ExpiredSignatureError, InvalidTokenError


@pytest.fixture
def security_manager():
    return SecurityManager()


def test_hash_password(security_manager):
    password = 'mysecretpassword'
    hashed_password = security_manager.hash_password(password)

    assert password != hashed_password
    assert security_manager.verify_password(password, hashed_password)


def test_create_access_token(security_manager):
    data = {'sub': 'test_user'}
    token = security_manager.create_access_token(data, expires_in=10)
    assert token is not None

    payload = security_manager.verify_access_token(token)
    assert payload['sub'] == 'test_user'
    assert 'exp' in payload


def test_token_expiration(security_manager):
    data = {'sub': 'test_user'}
    token = security_manager.create_access_token(data, expires_in=-1)

    with pytest.raises(ExpiredSignatureError):
        security_manager.verify_access_token(token)


def test_invalid_token(security_manager):
    invalid_token = 'invalid_token_example'

    with pytest.raises(InvalidTokenError):
        security_manager.verify_access_token(invalid_token)


def test_verify_password(security_manager):
    password = 'mysecretpassword'
    incorrect_password = 'wrongpassword'
    hashed_password = security_manager.hash_password(password)

    assert security_manager.verify_password(password, hashed_password)
    assert not security_manager.verify_password(incorrect_password, hashed_password)
