"""
Screenshot management utilities.

This module provides functionality for capturing, organizing, and managing
screenshots during bot execution for debugging and monitoring purposes.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.async_api import Page

from src.config.constants import (
    SCREENSHOT_FORMAT,
    SCREENSHOT_FULL_PAGE,
    SCREENSHOT_QUALITY,
    SCREENSHOTS_DIR,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScreenshotManager:
    """
    Manages screenshot capture and organization.

    Attributes:
        base_dir: Base directory for storing screenshots.
        session_dir: Directory for current session screenshots.
    """

    def __init__(self, base_dir: Path = SCREENSHOTS_DIR):
        """
        Initialize ScreenshotManager.

        Args:
            base_dir: Base directory for screenshots.
        """
        self.base_dir = base_dir
        self.session_dir: Optional[Path] = None
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure screenshot directories exist."""
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_session_directory(self, session_name: Optional[str] = None) -> Path:
        """
        Create a directory for the current session.

        Args:
            session_name: Optional name for the session. If not provided,
                         uses timestamp.

        Returns:
            Path to the session directory.
        """
        if session_name is None:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.session_dir = self.base_dir / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Created session directory: {self.session_dir}")
        return self.session_dir

    def get_screenshot_path(
        self,
        name: str,
        include_timestamp: bool = True,
        extension: str = SCREENSHOT_FORMAT,
    ) -> Path:
        """
        Generate a path for a screenshot.

        Args:
            name: Descriptive name for the screenshot.
            include_timestamp: Whether to include timestamp in filename.
            extension: File extension (default from constants).

        Returns:
            Path object for the screenshot file.
        """
        # Use session directory if available, otherwise base directory
        target_dir = self.session_dir if self.session_dir else self.base_dir

        # Sanitize name (replace spaces and special characters)
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

        # Add timestamp if requested
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.{extension}"
        else:
            filename = f"{safe_name}.{extension}"

        return target_dir / filename

    async def capture(
        self,
        page: Page,
        name: str,
        full_page: bool = SCREENSHOT_FULL_PAGE,
        quality: int = SCREENSHOT_QUALITY,
    ) -> Optional[Path]:
        """
        Capture a screenshot of the current page.

        Args:
            page: Playwright page instance.
            name: Descriptive name for the screenshot.
            full_page: Whether to capture full page or just viewport.
            quality: JPEG quality (0-100), only for JPEG format.

        Returns:
            Path to the saved screenshot, or None if failed.
        """
        try:
            screenshot_path = self.get_screenshot_path(name)

            # Capture screenshot
            await page.screenshot(
                path=str(screenshot_path),
                full_page=full_page,
                quality=quality if screenshot_path.suffix == ".jpg" else None,
            )

            logger.info(f"Screenshot saved: {screenshot_path.name}")
            return screenshot_path

        except Exception as e:
            logger.error(f"Failed to capture screenshot '{name}': {e}")
            return None

    async def capture_element(
        self,
        page: Page,
        selector: str,
        name: str,
    ) -> Optional[Path]:
        """
        Capture a screenshot of a specific element.

        Args:
            page: Playwright page instance.
            selector: CSS selector for the element.
            name: Descriptive name for the screenshot.

        Returns:
            Path to the saved screenshot, or None if failed.
        """
        try:
            screenshot_path = self.get_screenshot_path(name)

            element = page.locator(selector).first
            await element.screenshot(path=str(screenshot_path))

            logger.info(f"Element screenshot saved: {screenshot_path.name}")
            return screenshot_path

        except Exception as e:
            logger.error(
                f"Failed to capture element screenshot '{name}' for '{selector}': {e}"
            )
            return None

    async def capture_on_error(
        self,
        page: Page,
        error_type: str,
        exception: Optional[Exception] = None,
    ) -> Optional[Path]:
        """
        Capture a screenshot when an error occurs.

        Args:
            page: Playwright page instance.
            error_type: Type/category of error.
            exception: The exception that occurred (optional).

        Returns:
            Path to the saved screenshot, or None if failed.
        """
        error_name = f"error_{error_type}"

        if exception:
            logger.error(f"Capturing error screenshot for: {exception}")

        return await self.capture(page, error_name, full_page=True)

    async def capture_sequence(
        self,
        page: Page,
        base_name: str,
        count: int,
    ) -> list[Path]:
        """
        Capture a sequence of screenshots (e.g., for a multi-step process).

        Args:
            page: Playwright page instance.
            base_name: Base name for the screenshot sequence.
            count: Current step number in the sequence.

        Returns:
            List of paths to saved screenshots.
        """
        name = f"{base_name}_{count:02d}"
        result = await self.capture(page, name)
        return [result] if result else []

    def cleanup_old_screenshots(self, days: int = 7) -> int:
        """
        Remove screenshots older than specified days.

        Args:
            days: Number of days to keep screenshots.

        Returns:
            Number of files deleted.
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days * 86400)
            deleted_count = 0

            for screenshot_file in self.base_dir.rglob(f"*.{SCREENSHOT_FORMAT}"):
                if screenshot_file.stat().st_mtime < cutoff_time:
                    screenshot_file.unlink()
                    deleted_count += 1

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old screenshots")

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old screenshots: {e}")
            return 0

    def get_session_screenshots(self) -> list[Path]:
        """
        Get all screenshots from the current session.

        Returns:
            List of screenshot file paths.
        """
        if not self.session_dir or not self.session_dir.exists():
            return []

        return sorted(
            self.session_dir.glob(f"*.{SCREENSHOT_FORMAT}"),
            key=lambda p: p.stat().st_mtime,
        )

    def count_screenshots(self) -> int:
        """
        Count total number of screenshots.

        Returns:
            Total screenshot count.
        """
        return len(list(self.base_dir.rglob(f"*.{SCREENSHOT_FORMAT}")))


# Singleton instance
_screenshot_manager: Optional[ScreenshotManager] = None


def get_screenshot_manager() -> ScreenshotManager:
    """
    Get the singleton ScreenshotManager instance.

    Returns:
        ScreenshotManager instance.
    """
    global _screenshot_manager
    if _screenshot_manager is None:
        _screenshot_manager = ScreenshotManager()
    return _screenshot_manager
