from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.user_service import UserService
from app.types.schemas import ResponseCreate, UserPayload, UserResponse

router = APIRouter(prefix='/user')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreate[UserResponse],
)
def create_user(
    user: UserPayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = UserService(session)
    db_user = service.user_register(user)
    public_user = UserResponse.model_validate(db_user.to_dict())
    return ResponseCreate(message='User created with success.', data=public_user)
