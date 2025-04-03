import logging
from typing import List, Optional

from app.core.database import get_session
from app.core.events import event_bus
from app.user.auth import create_access_token, get_password_hash, verify_password
from app.user.models import User, UserRole
from app.user.repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Service untuk manajemen user dan autentikasi."""

    def __init__(self):
        """Initialize user service."""
        # Subscribe to app startup event untuk membuat admin default
        event_bus.subscribe("app.startup", self.on_app_startup)

    async def on_app_startup(self):
        """Create default admin user on application startup."""
        logger.info("Ensuring default admin user exists")
        await self.ensure_admin_user()

    async def ensure_admin_user(self) -> None:
        """Ensure default admin user exists in the system."""
        admin_username = "admin"

        with get_session() as session:
            repository = UserRepository(session)
            admin = repository.get_by_username(admin_username)

            if not admin:
                logger.info("Creating default admin user")
                admin = User(
                    username=admin_username,
                    hashed_password=get_password_hash("admin"),
                    full_name="System Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
                repository.create(admin)
                logger.info("Default admin user created successfully")

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.

        Args:
            username: User's username
            password: User's password

        Returns:
            User object if authentication successful, None otherwise
        """
        with get_session() as session:
            repository = UserRepository(session)
            user = repository.get_by_username(username)

            if not user:
                logger.warning(f"Authentication failed: User {username} not found")
                return None

            if not user.is_active:
                logger.warning(f"Authentication failed: User {username} is inactive")
                return None

            if not verify_password(password, user.hashed_password):
                logger.warning(
                    f"Authentication failed: Invalid password for {username}"
                )
                return None

            # Update last login time
            if user.id is not None:
                repository.update_last_login(user.id)
            else:
                logger.warning(
                    f"Cannot update last login: User ID is None for {username}"
                )

            return user

    async def create_token(self, user: User) -> str:
        """
        Create access token for user.

        Args:
            user: User object

        Returns:
            JWT access token
        """
        token_data = {"sub": user.username, "id": user.id, "role": user.role}
        return create_access_token(token_data)

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        with get_session() as session:
            repository = UserRepository(session)
            return repository.get_all(skip, limit)

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        with get_session() as session:
            repository = UserRepository(session)
            return repository.get_by_id(user_id)

    async def create_user(
        self,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        role: UserRole = UserRole.VIEWER,
    ) -> Optional[User]:
        """Create a new user."""
        with get_session() as session:
            repository = UserRepository(session)

            # Check if username already exists
            existing_user = repository.get_by_username(username)
            if existing_user:
                logger.warning(
                    f"Cannot create user: Username {username} already exists"
                )
                return None

            user = User(
                username=username,
                hashed_password=get_password_hash(password),
                full_name=full_name,
                email=email,
                role=role,
            )

            return repository.create(user)


# Create singleton instance
user_service = UserService()
