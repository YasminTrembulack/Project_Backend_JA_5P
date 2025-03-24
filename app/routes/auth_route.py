from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.services.auth_service import AuthService
from app.types.schemas import LoginPayload, LoginResponse, UserPublic

router = APIRouter()


@router.post('/login', status_code=status.HTTP_200_OK, response_model=LoginResponse)
def login(user: LoginPayload, session: Session = Depends(get_session)):
    service = AuthService(session)
    token, _user = service.login(user)
    return LoginResponse(
        message='Login successful!',
        token=token,
        user=UserPublic.model_validate(_user.to_dict()),
    )
