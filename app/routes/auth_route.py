from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.auth_service import AuthService
from app.types.schemas import LoginPayload, LoginResponse, RefreshTokenResponse, UserResponse

router = APIRouter()


@router.post('/login', status_code=status.HTTP_200_OK, response_model=LoginResponse)
def login(user: LoginPayload, session: Session = Depends(get_session)):
    service = AuthService(session)
    access_token, refresh_token, _user = service.login(user)
    return LoginResponse(
        message='Login successful!',
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(_user.to_dict()),
    )

@router.post(
    '/refresh_token',
    status_code=status.HTTP_200_OK,
    response_model=RefreshTokenResponse
)
def refresh_token(
    session: Session = Depends(get_session),
    user: None = Depends(check_roles(['Admin', 'User', 'Editor']))
):
    service = AuthService(session)
    new_access_token = service.refresh_token(user.id)

    return RefreshTokenResponse(
        message='Access token refreshed successfully!',
        access_token=new_access_token,
    )
