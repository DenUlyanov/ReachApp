"""
Logging configuration with rotation and color support.

This module provides a centralized logging setup with console colors,
file rotation, and customizable formatting.
"""

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from src.config.constants import (
    COLORED_LOG_FORMAT,
    LOG_BACKUP_COUNT,
    LOG_COLORS,
    LOG_DATE_FORMAT,
    LOG_FILE_PREFIX,
    LOG_FILE_SUFFIX,
    LOG_FORMAT,
    LOG_LEVEL_INFO,
    LOG_MAX_BYTES,
    LOG_TIMESTAMP_FORMAT,
    LOGS_DIR,
)

# Try to import colorlog for colored console output
try:
    import colorlog

    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


class BotLogger:
    """
    Centralized logger for the LinkedIn Bot.

    Provides colored console output and rotating file logs.
    """

    _instance: Optional["BotLogger"] = None
    _loggers: dict[str, logging.Logger] = {}

    def __new__(cls) -> "BotLogger":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the logger (only once due to singleton)."""
        if self._initialized:
            return

        self._initialized = True
        self._setup_log_directory()

    def _setup_log_directory(self) -> None:
        """Ensure the logs directory exists."""
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def get_logger(
        self,
        name: str,
        level: str = LOG_LEVEL_INFO,
        log_to_file: bool = True,
        log_to_console: bool = True,
    ) -> logging.Logger:
        """
        Get or create a logger with the specified configuration.

        Args:
            name: Logger name (typically __name__ of the module).
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            log_to_file: Whether to log to a file.
            log_to_console: Whether to log to console.

        Returns:
            Configured logger instance.
        """
        # Return cached logger if it exists
        if name in self._loggers:
            return self._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        logger.handlers.clear()  # Remove any existing handlers
        logger.propagate = False  # Don't propagate to root logger

        # Add console handler
        if log_to_console:
            console_handler = self._create_console_handler()
            logger.addHandler(console_handler)

        # Add file handler
        if log_to_file:
            file_handler = self._create_file_handler()
            logger.addHandler(file_handler)

        # Cache the logger
        self._loggers[name] = logger

        return logger

    def _create_console_handler(self) -> logging.Handler:
        """
        Create a colored console handler.

        Returns:
            Configured console handler.
        """
        console_handler = logging.StreamHandler(sys.stdout)

        if HAS_COLORLOG:
            # Use colored formatter
            formatter = colorlog.ColoredFormatter(
                COLORED_LOG_FORMAT,
                datefmt=LOG_DATE_FORMAT,
                log_colors=LOG_COLORS,
            )
        else:
            # Fallback to standard formatter
            formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

        console_handler.setFormatter(formatter)
        return console_handler

    def _create_file_handler(self) -> logging.Handler:
        """
        Create a rotating file handler.

        Returns:
            Configured file handler.
        """
        timestamp = datetime.now().strftime(LOG_TIMESTAMP_FORMAT)
        log_file = LOGS_DIR / f"{LOG_FILE_PREFIX}_{timestamp}{LOG_FILE_SUFFIX}"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )

        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        file_handler.setFormatter(formatter)

        return file_handler

    def set_level(self, logger_name: str, level: str) -> None:
        """
        Change the logging level for a specific logger.

        Args:
            logger_name: Name of the logger.
            level: New logging level.
        """
        if logger_name in self._loggers:
            logger = self._loggers[logger_name]
            logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    def set_all_levels(self, level: str) -> None:
        """
        Change the logging level for all loggers.

        Args:
            level: New logging level.
        """
        for logger in self._loggers.values():
            logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    @classmethod
    def cleanup(cls) -> None:
        """Close all file handlers and clear cached loggers."""
        for logger in cls._loggers.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        cls._loggers.clear()


# Singleton instance
_bot_logger: Optional[BotLogger] = None


def get_logger(
    name: str,
    level: str = LOG_LEVEL_INFO,
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> logging.Logger:
    """
    Get a configured logger instance.

    This is the main function to use for getting loggers throughout the application.

    Args:
        name: Logger name (use __name__ for module-level logging).
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_to_file: Whether to write logs to a file.
        log_to_console: Whether to print logs to console.

    Returns:
        Configured logger instance.

    Example:
        ```python
        from src.utils.logger import get_logger

        logger = get_logger(__name__)
        logger.info("This is an info message")
        logger.error("This is an error message")
        ```
    """
    global _bot_logger
    if _bot_logger is None:
        _bot_logger = BotLogger()
    return _bot_logger.get_logger(name, level, log_to_file, log_to_console)


def set_log_level(logger_name: str, level: str) -> None:
    """
    Change the logging level for a specific logger.

    Args:
        logger_name: Name of the logger to modify.
        level: New logging level.
    """
    if _bot_logger:
        _bot_logger.set_level(logger_name, level)


def set_all_log_levels(level: str) -> None:
    """
    Change the logging level for all active loggers.

    Args:
        level: New logging level.
    """
    if _bot_logger:
        _bot_logger.set_all_levels(level)


def cleanup_loggers() -> None:
    """Close all file handlers and clean up resources."""
    if _bot_logger:
        BotLogger.cleanup()
