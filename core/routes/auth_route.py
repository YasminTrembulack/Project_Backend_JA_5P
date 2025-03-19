from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.controllers.auth_controller import AuthController
from core.db.database import get_session
from core.types.schemas import LoginPayload, LoginResponse, UserPublic

router = APIRouter()


@router.post(
    '/login',
    status_code=HTTPStatus.OK,
    response_model=LoginResponse
)
def login(user: LoginPayload, session: Session = Depends(get_session)):
    controller = AuthController(session)
    token, _user = controller.login(user)
    return LoginResponse(
        message='Login successful!',
        token=token,
        user=UserPublic.model_validate(_user.to_dict())
    )
