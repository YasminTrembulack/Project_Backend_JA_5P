from typing import List, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.user_service import UserService
from app.types.base import Metadata
from app.types.payload import (
    UserPayload,
    UserQueryParams,
    UserUpdatePayload,
)
from app.types.response import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    UserResponse,
)

router = APIRouter(prefix='/user')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[UserResponse],
)
def create_user(
    user: UserPayload,
    session: Session = Depends(get_session),
    # _: None = Depends(check_roles(['Admin'])),
):
    service = UserService(session)
    db_user = service.user_register(user)
    user_response = UserResponse.model_validate(db_user.to_dict())
    return EntityResponse(message='User created with success.', data=user_response)


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[UserResponse],
)
def get_all_users(
    query: UserQueryParams = Depends(),
    associations: List[Literal['molds_created']] = Query([]),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = UserService(session)
    users, total_users = service.get_all_users(query)
    total_pages = (total_users + query.limit - 1) // query.limit
    meta = Metadata(
        total=total_users,
        limit=query.limit,
        page=query.page,
        total_pages=total_pages,
        has_next=query.page < total_pages,
        has_previous=query.page > 1,
        order_by=query.order_by,
        desc_order=query.desc_order,
    )

    user_reponse = []

    for u in users:
        user_dict = u.to_dict()
        associations_dict = service.configure_associations_response(u, associations)
        combined_dict = {**user_dict, **associations_dict}

        user_reponse.append(UserResponse.model_validate(combined_dict))

    return GetAllResponse(
        message='Users found successfully.', data=user_reponse, metadata=meta
    )


@router.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK,
    response_model=DeleteResponse,
)
def delete_user(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'], True)),
):
    service = UserService(session)
    service.delete_user(id)
    return DeleteResponse(message='User deleted successfully.')


@router.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[UserResponse],
)
def update_user(
    id: str,
    user: UserUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'], True)),
):
    service = UserService(session)
    user = service.update_user(id, user)
    user_response = UserResponse.model_validate(user.to_dict())
    return EntityResponse(message='User updated successfully.', data=user_response)


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[UserResponse],
)
def get_user(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = UserService(session)
    user = service.get_user(id)
    user_response = UserResponse.model_validate(user.to_dict())
    return EntityResponse(message='User found successfully.', data=user_response)
