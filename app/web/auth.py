import logging
from typing import Optional

from fastapi import Request
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import AUTH_ALGORITHM, AUTH_SECRET_KEY
from app.core.database import get_session
from app.user.repository import UserRepository

logger = logging.getLogger(__name__)


async def get_user_from_token(token: str) -> Optional[dict]:
    """Get user data from token."""
    try:
        payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
        username = payload.get("sub")
        if not isinstance(username, str):
            return None
        if not username:
            return None

        with get_session() as session:
            repository = UserRepository(session)
            user = repository.get_by_username(username)

        if not user:
            return None

        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
        }
    except JWTError:
        return None
    except Exception as e:
        logger.error(f"Error getting user from token: {e}", exc_info=True)
        return None


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication on web routes."""

    # Paths that don't require authentication
    PUBLIC_PATHS = {"/", "/login", "/register", "/logout", "/static", "/api/auth/login"}

    # API paths handled separately by OAuth2 dependencies
    API_PATHS = {"/api/"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        """Process request and check for authentication."""
        path = request.url.path

        # Skip auth for public paths
        if any(
            path == public_path or path.startswith(public_path)
            for public_path in self.PUBLIC_PATHS
        ):
            return await call_next(request)

        # For API paths, let OAuth2 dependencies handle it
        if any(path.startswith(api_path) for api_path in self.API_PATHS):
            return await call_next(request)

        # Check cookie for auth token
        token = request.cookies.get("access_token")
        if not token:
            logger.debug(f"No token found for protected path: {path}")
            return RedirectResponse("/login")

        # Validate token
        user = await get_user_from_token(token)
        if not user:
            logger.debug(f"Invalid token for protected path: {path}")
            response = RedirectResponse("/login")
            response.delete_cookie(key="access_token")
            return response

        # Add user to request state for access in templates
        request.state.user = user

        # Continue processing
        return await call_next(request)
