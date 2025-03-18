from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.db.database import get_session
from core.models.user import User
from core.types.schemas import ResponseCreate, UserPublic, UserSchema

router = APIRouter()


@router.post(
    '/user',
    status_code=HTTPStatus.CREATED,
    response_model=ResponseCreate[UserPublic]
)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    user_found = session.scalar(
        select(User).where(
            (User.email == user.email)
        )
    )
    if user_found:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            detail='Email alredy exists.'
        )
    db_user = User(
        full_name=user.full_name, password=user.password, email=user.email
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    public_user = UserPublic.model_validate(db_user.to_dict())
    return {'message': 'User created with success.', 'data': public_user}
