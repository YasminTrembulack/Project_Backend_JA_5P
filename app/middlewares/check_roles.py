from typing import List

from fastapi import Depends, Request

from app.models.user import User
from app.types.exceptions import NotAuthenticatedError, PermissionDeniedError


def get_current_user(request: Request):
    if not hasattr(request.state, 'user') or request.state.user is None:
        raise NotAuthenticatedError('Not authenticated')
    return request.state.user


def check_roles(required_roles: List[str], self_action: bool = False):
    def role_dependency(id: str = None, user: User = Depends(get_current_user)):
        if user.role in required_roles:
            return user
        if self_action and user.id == id:
            return user
        raise PermissionDeniedError(
            f'Permission denied, only {", ".join(required_roles)} '
            f'{("or the user with the corresponding ID " if self_action else "")}'
            'allowed.'
        )

    return role_dependency
