from sqlalchemy.orm import Session

from app.core.security import security
from app.interfaces.user_repository_interface import IUserRepository
from app.models.user import User
from app.types.schemas import UserPayload


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserPayload) -> User:
        hashed_password = security.hash_password(user.password)
        db_user = User(
            full_name=user.full_name,
            password=hashed_password,
            email=user.email,
            registration_number=user.registration_number,
            role=user.role,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_registration_number(self, re: str) -> User | None:
        return self.db.query(User).filter(User.registration_number == re).first()

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
