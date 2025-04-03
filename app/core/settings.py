import datetime
import logging
from typing import Dict, Optional

from sqlmodel import Session, select

from app.core.database import get_session
from app.core.models import Setting

logger = logging.getLogger(__name__)

# Default settings yang akan dimasukkan ke database jika belum ada
DEFAULT_SETTINGS = {
    "adb_path": "",
    "device_poll_interval": "10",
    "adb_server_timeout": "30",
}


class SettingsManager:
    """Manager untuk settings aplikasi."""

    def __init__(self):
        """Initialize settings manager."""
        self._cache: Dict[str, str] = {}
        self._loaded = False

    def load_settings(self) -> None:
        """Load all settings from database."""
        if self._loaded:
            return

        logger.info("Loading settings from database")
        try:
            with get_session() as session:
                self._ensure_default_settings(session)

                # Load all settings to cache
                statement = select(Setting)
                settings = session.exec(statement).all()

                for setting in settings:
                    self._cache[setting.key] = setting.value

                self._loaded = True
                logger.info(f"Loaded {len(settings)} settings from database")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            # Fallback to defaults if database access fails
            for key, value in DEFAULT_SETTINGS.items():
                self._cache[key] = value
            logger.info("Using default settings due to database error")
            self._loaded = True

    def _ensure_default_settings(self, session: Session) -> None:
        """Ensure default settings exist in database."""
        for key, value in DEFAULT_SETTINGS.items():
            try:
                statement = select(Setting).where(Setting.key == key)
                setting = session.exec(statement).first()

                if setting is None:
                    # Create with default value
                    setting = Setting(
                        key=key, value=value, description=f"Default setting for {key}"
                    )
                    session.add(setting)
                    logger.debug(f"Created default setting: {key}={value}")
            except Exception as e:
                logger.error(f"Error ensuring default setting {key}: {e}")

        session.commit()

    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get setting value by key."""
        if not self._loaded:
            self.load_settings()

        # Use provided default if key not in cache
        return self._cache.get(key, default or DEFAULT_SETTINGS.get(key, "") or "")

    def set(self, key: str, value: str, description: Optional[str] = None) -> None:
        """Set setting value."""
        try:
            with get_session() as session:
                statement = select(Setting).where(Setting.key == key)
                setting = session.exec(statement).first()

                if setting:
                    setting.value = value
                    if description:
                        setting.description = description
                    setting.updated_at = datetime.datetime.now()
                else:
                    setting = Setting(
                        key=key,
                        value=value,
                        description=description or f"Setting for {key}",
                    )
                    session.add(setting)

                session.commit()

                # Update cache
                self._cache[key] = value
                logger.info(f"Updated setting: {key}={value}")
        except Exception as e:
            logger.error(f"Error setting {key}={value}: {e}")
            # Update cache anyway
            self._cache[key] = value


# Singleton instance
settings_manager = SettingsManager()
