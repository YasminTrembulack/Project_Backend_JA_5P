from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repositorie import UserRepository
from app.types.exceptions import DataConflictError
from app.types.exceptions import DataConflictError
from app.types.schemas import UserSchema


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def user_register(self, user: UserSchema) -> User:
        user_found = self.user_repo.get_user_by_email(user.email)
        user_found = self.user_repo.get_user_by_registration_number(
            user.registration_number
        )
        if user_found:
            raise DataConflictError(
                'Email alredy in use.'
            raise DataConflictError(
                'Email alredy in use.'
                if user.email == user_found.email
                else 'Registration number alredy in use.'
                else 'Registration number alredy in use.'
            )
        return self.user_repo.create_user(user)
