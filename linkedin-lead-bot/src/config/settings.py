"""
Configuration management using Pydantic settings.

This module handles loading configuration from environment variables (.env)
and YAML files, with validation and type checking.
"""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.constants import (
    CONFIG_DIR,
    DEFAULT_GEOLOCATION,
    DEFAULT_LOCALE,
    DEFAULT_TIMEOUT,
    DEFAULT_TIMEZONE,
    DEFAULT_USER_AGENT,
    DEFAULT_VIEWPORT_HEIGHT,
    DEFAULT_VIEWPORT_WIDTH,
    ENV_HEADLESS_MODE,
    ENV_LINKEDIN_EMAIL,
    ENV_LINKEDIN_PASSWORD,
    ENV_LOG_LEVEL,
    ENV_MAX_LOGIN_ATTEMPTS,
    ENV_SALES_NAVIGATOR_URL,
    ENV_SLOW_MO,
    ENV_TIMEOUT,
    LOG_LEVEL_INFO,
    MAX_RETRY_ATTEMPTS,
    SALES_NAVIGATOR_BASE_URL,
    SELECTORS_FILE,
    SETTINGS_FILE,
)
from src.exceptions import ConfigurationException


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and YAML files.

    Attributes:
        linkedin_email: LinkedIn account email.
        linkedin_password: LinkedIn account password.
        sales_navigator_url: Sales Navigator URL.
        headless: Whether to run browser in headless mode.
        slow_mo: Slow motion delay in milliseconds (for debugging).
        timeout: Default timeout in milliseconds.
        max_login_attempts: Maximum number of login retry attempts.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        _settings_yaml: Cached settings from YAML file.
        _selectors_yaml: Cached selectors from YAML file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LinkedIn credentials
    linkedin_email: str = Field(
        default="",
        alias=ENV_LINKEDIN_EMAIL,
        description="LinkedIn account email",
    )
    linkedin_password: str = Field(
        default="",
        alias=ENV_LINKEDIN_PASSWORD,
        description="LinkedIn account password",
    )
    sales_navigator_url: str = Field(
        default=SALES_NAVIGATOR_BASE_URL,
        alias=ENV_SALES_NAVIGATOR_URL,
        description="Sales Navigator URL",
    )

    # Browser settings
    headless: bool = Field(
        default=False,
        alias=ENV_HEADLESS_MODE,
        description="Run browser in headless mode",
    )
    slow_mo: int = Field(
        default=0,
        alias=ENV_SLOW_MO,
        description="Slow motion delay in milliseconds",
        ge=0,
        le=5000,
    )

    # Timeout settings
    timeout: int = Field(
        default=DEFAULT_TIMEOUT,
        alias=ENV_TIMEOUT,
        description="Default timeout in milliseconds",
        ge=1000,
        le=300000,
    )

    # Retry settings
    max_login_attempts: int = Field(
        default=MAX_RETRY_ATTEMPTS,
        alias=ENV_MAX_LOGIN_ATTEMPTS,
        description="Maximum login retry attempts",
        ge=1,
        le=10,
    )

    # Logging settings
    log_level: str = Field(
        default=LOG_LEVEL_INFO,
        alias=ENV_LOG_LEVEL,
        description="Logging level",
    )

    # Cached YAML configurations
    _settings_yaml: dict[str, Any] | None = None
    _selectors_yaml: dict[str, Any] | None = None

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate and normalize log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of {allowed_levels}"
            )
        return v_upper

    @field_validator("linkedin_email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @model_validator(mode="after")
    def validate_credentials(self) -> "Settings":
        """Ensure credentials are provided for production use."""
        if not self.linkedin_email or not self.linkedin_password:
            # Allow empty credentials for testing
            if os.getenv("TESTING") != "true":
                import warnings

                warnings.warn(
                    "LinkedIn credentials not configured in .env file. "
                    "Bot functionality will be limited.",
                    UserWarning,
                    stacklevel=2,
                )
        return self

    def load_settings_yaml(self) -> dict[str, Any]:
        """
        Load settings from YAML file.

        Returns:
            Dictionary containing settings from YAML file.

        Raises:
            ConfigurationException: If YAML file cannot be loaded.
        """
        if self._settings_yaml is not None:
            return self._settings_yaml

        settings_path = SETTINGS_FILE
        if not settings_path.exists():
            raise ConfigurationException(
                f"Settings file not found: {settings_path}",
                config_key="settings_yaml",
            )

        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                self._settings_yaml = yaml.safe_load(f) or {}
            return self._settings_yaml
        except yaml.YAMLError as e:
            raise ConfigurationException(
                f"Failed to parse settings YAML: {e}",
                config_key="settings_yaml",
            ) from e
        except Exception as e:
            raise ConfigurationException(
                f"Failed to load settings YAML: {e}",
                config_key="settings_yaml",
            ) from e

    def load_selectors_yaml(self) -> dict[str, Any]:
        """
        Load UI selectors from YAML file.

        Returns:
            Dictionary containing selectors from YAML file.

        Raises:
            ConfigurationException: If YAML file cannot be loaded.
        """
        if self._selectors_yaml is not None:
            return self._selectors_yaml

        selectors_path = SELECTORS_FILE
        if not selectors_path.exists():
            raise ConfigurationException(
                f"Selectors file not found: {selectors_path}",
                config_key="selectors_yaml",
            )

        try:
            with open(selectors_path, "r", encoding="utf-8") as f:
                self._selectors_yaml = yaml.safe_load(f) or {}
            return self._selectors_yaml
        except yaml.YAMLError as e:
            raise ConfigurationException(
                f"Failed to parse selectors YAML: {e}",
                config_key="selectors_yaml",
            ) from e
        except Exception as e:
            raise ConfigurationException(
                f"Failed to load selectors YAML: {e}",
                config_key="selectors_yaml",
            ) from e

    def get_delay_config(self) -> dict[str, Any]:
        """
        Get delay configuration from YAML.

        Returns:
            Dictionary with delay settings.
        """
        settings = self.load_settings_yaml()
        return settings.get("delays", {})

    def get_browser_config(self) -> dict[str, Any]:
        """
        Get browser configuration from YAML.

        Returns:
            Dictionary with browser settings.
        """
        settings = self.load_settings_yaml()
        return settings.get("browser", {})

    def get_selectors(self, page_name: str) -> dict[str, str]:
        """
        Get selectors for a specific page.

        Args:
            page_name: Name of the page (e.g., 'login_page', 'feed_page').

        Returns:
            Dictionary of selectors for the page.

        Raises:
            ConfigurationException: If page selectors not found.
        """
        selectors = self.load_selectors_yaml()
        if page_name not in selectors:
            raise ConfigurationException(
                f"Selectors not found for page: {page_name}",
                config_key=page_name,
            )
        return selectors[page_name]

    @property
    def viewport_size(self) -> dict[str, int]:
        """Get viewport size from browser config."""
        browser_config = self.get_browser_config()
        return {
            "width": browser_config.get("viewport_width", DEFAULT_VIEWPORT_WIDTH),
            "height": browser_config.get("viewport_height", DEFAULT_VIEWPORT_HEIGHT),
        }

    @property
    def user_agent(self) -> str:
        """Get user agent from browser config."""
        browser_config = self.get_browser_config()
        return browser_config.get("user_agent", DEFAULT_USER_AGENT)

    @property
    def locale(self) -> str:
        """Get locale from browser config."""
        browser_config = self.get_browser_config()
        return browser_config.get("locale", DEFAULT_LOCALE)

    @property
    def timezone(self) -> str:
        """Get timezone from browser config."""
        browser_config = self.get_browser_config()
        return browser_config.get("timezone", DEFAULT_TIMEZONE)

    @property
    def geolocation(self) -> dict[str, float]:
        """Get geolocation from browser config."""
        browser_config = self.get_browser_config()
        return browser_config.get("geolocation", DEFAULT_GEOLOCATION)


# Singleton instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get the singleton Settings instance.

    Returns:
        Settings instance.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings (useful for testing).

    Returns:
        New Settings instance.
    """
    global _settings
    _settings = Settings()
    return _settings
