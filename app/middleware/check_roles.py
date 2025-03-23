
from fastapi import Depends, Request

from app.models.user import User
from app.types.exceptions import NotAuthenticatedError, PermissionDeniedError


def get_current_user(request: Request):
    if not hasattr(request.state, "user") or request.state.user is None:
        raise NotAuthenticatedError("Not authenticated")
    return request.state.user


def check_roles(required_roles: list):
    def role_dependency(user: User = Depends(get_current_user)):
        if user.role not in required_roles:
            raise PermissionDeniedError(
                f"Permission denied, only {', '.join(required_roles)} allowed."
            )
        return user
    return role_dependency
