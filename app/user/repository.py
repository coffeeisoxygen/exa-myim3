from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from app.user.models import User


class UserRepository:
    """Repository untuk operasi database user."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        statement = select(User).offset(skip).limit(limit)
        return list(self.session.exec(statement))

    def create(self, user: User) -> User:
        """Create new user."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Update existing user."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.session.delete(user)
        self.session.commit()
        return True

    def update_last_login(self, user_id: int) -> Optional[User]:
        """Update user's last login time."""
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.last_login = datetime.now()
        return self.update(user)
