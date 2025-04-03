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

        with get_session() as session:
            self._ensure_default_settings(session)

            # Load all settings to cache
            statement = select(Setting)
            settings = session.exec(statement).all()

            for setting in settings:
                self._cache[setting.key] = setting.value

            self._loaded = True
            logger.info(f"Loaded {len(settings)} settings from database")

    def _ensure_default_settings(self, session: Session) -> None:
        """Ensure default settings exist in database."""
        for key, value in DEFAULT_SETTINGS.items():
            statement = select(Setting).where(Setting.key == key)
            setting = session.exec(statement).first()

            if setting is None:
                # Create with default value
                setting = Setting(
                    key=key, value=value, description=f"Default setting for {key}"
                )
                session.add(setting)

        session.commit()

    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get setting value by key."""
        if not self._loaded:
            self.load_settings()

        return self._cache.get(key, default or "")

    def set(self, key: str, value: str, description: Optional[str] = None) -> None:
        """Set setting value."""
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


# Singleton instance
settings_manager = SettingsManager()
