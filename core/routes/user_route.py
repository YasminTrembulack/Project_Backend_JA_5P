from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.controllers.user_controller import UserController
from core.db.database import get_session
from core.types.schemas import ResponseCreate, UserPublic, UserSchema

router = APIRouter(prefix='/user')


@router.post(
    '/register',
    status_code=HTTPStatus.CREATED,
    response_model=ResponseCreate[UserPublic]
)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    controller = UserController(session)
    db_user = controller.user_register(user)
    public_user = UserPublic.model_validate(db_user.to_dict())
    return ResponseCreate(
        message='User created with success.',
        data=public_user
    )
