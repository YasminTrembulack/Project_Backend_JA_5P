import pytest

from app.core.security import SecurityManager
from app.types.exceptions import ExpiredSignatureError, InvalidTokenError


@pytest.fixture
def security_manager():
    return SecurityManager()


# Testando o hash da senha
def test_hash_password(security_manager):
    password = 'mysecretpassword'
    hashed_password = security_manager.hash_password(password)

    # Verificando se o hash gerado não é o mesmo da senha original
    assert password != hashed_password
    assert security_manager.verify_password(password, hashed_password)
    # Deve verificar corretamente


# Testando a criação de um token de acesso
def test_create_access_token(security_manager):
    data = {'sub': 'test_user'}
    token = security_manager.create_access_token(data, expires_in=10)
    # Token válido por 10 minutos

    # Verificando se o token foi gerado
    assert token is not None

    # Decodificando o token para ver a carga útil
    payload = security_manager.verify_access_token(token)

    assert payload['sub'] == 'test_user'
    assert 'exp' in payload
    # Certificando-se que a expiração foi adicionada ao token


# Testando a expiração do token
def test_token_expiration(security_manager):
    data = {'sub': 'test_user'}
    token = security_manager.create_access_token(data, expires_in=-1)
    # Criando um token já expirado

    # Verificando se o token expira e levanta o erro correto
    with pytest.raises(ExpiredSignatureError):
        security_manager.verify_access_token(token)


# Testando token inválido
def test_invalid_token(security_manager):
    invalid_token = 'invalid_token_example'

    # Verificando se um token inválido levanta o erro correto
    with pytest.raises(InvalidTokenError):
        security_manager.verify_access_token(invalid_token)


# Testando a verificação da senha
def test_verify_password(security_manager):
    password = 'mysecretpassword'
    hashed_password = security_manager.hash_password(password)

    # Senha correta
    assert security_manager.verify_password(password, hashed_password)

    # Senha incorreta
    incorrect_password = 'wrongpassword'
    assert not security_manager.verify_password(incorrect_password, hashed_password)
