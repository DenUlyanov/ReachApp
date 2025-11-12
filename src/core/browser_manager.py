"""
Browser manager with singleton pattern and anti-detection features.

This module provides a centralized browser management system with
comprehensive stealth configurations to avoid detection.
"""

from typing import Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from src.config.constants import (
    DEFAULT_BROWSER_ARGS,
    DEFAULT_GEOLOCATION,
    DEFAULT_LOCALE,
    DEFAULT_TIMEZONE,
    DEFAULT_USER_AGENT,
    DEFAULT_VIEWPORT_HEIGHT,
    DEFAULT_VIEWPORT_WIDTH,
    NON_HEADLESS_ARGS,
)
from src.config.settings import Settings, get_settings
from src.exceptions import BrowserInitializationException
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BrowserManager:
    """
    Singleton browser manager with anti-detection configurations.

    This class manages the Playwright browser instance, context, and pages
    with comprehensive stealth features to avoid bot detection.

    Attributes:
        _instance: Singleton instance.
        _playwright: Playwright instance.
        _browser: Browser instance.
        _context: Browser context.
        _page: Current page.
        _settings: Configuration settings.
    """

    _instance: Optional["BrowserManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "BrowserManager":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize BrowserManager (only once due to singleton)."""
        if BrowserManager._initialized:
            return

        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._settings: Settings = get_settings()

        BrowserManager._initialized = True
        logger.debug("BrowserManager singleton created")

    @classmethod
    async def get_instance(cls) -> "BrowserManager":
        """
        Get the singleton BrowserManager instance.

        Returns:
            BrowserManager instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(
        self,
        headless: Optional[bool] = None,
        slow_mo: Optional[int] = None,
        viewport: Optional[dict[str, int]] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Initialize the browser with anti-detection configurations.

        Args:
            headless: Run browser in headless mode (overrides settings).
            slow_mo: Slow motion delay in milliseconds (overrides settings).
            viewport: Custom viewport size (overrides settings).
            user_agent: Custom user agent (overrides settings).

        Raises:
            BrowserInitializationException: If browser initialization fails.
        """
        if self._browser is not None:
            logger.warning("Browser already initialized")
            return

        try:
            logger.info("Initializing browser with anti-detection features...")

            # Use provided values or fall back to settings
            headless_mode = (
                headless if headless is not None else self._settings.headless
            )
            slow_motion = (
                slow_mo if slow_mo is not None else self._settings.slow_mo
            )

            # Start Playwright
            self._playwright = await async_playwright().start()

            # Prepare browser arguments
            browser_args = DEFAULT_BROWSER_ARGS.copy()

            # Add non-headless specific args
            if not headless_mode:
                browser_args.extend(NON_HEADLESS_ARGS)

            # Launch browser
            self._browser = await self._playwright.chromium.launch(
                headless=headless_mode,
                args=browser_args,
                slow_mo=slow_motion,
            )

            logger.info(f"Browser launched (headless={headless_mode})")

            # Prepare context options
            viewport_size = viewport or self._settings.viewport_size
            ua = user_agent or self._settings.user_agent

            # Create context with realistic settings
            self._context = await self._browser.new_context(
                viewport=viewport_size if headless_mode else None,
                user_agent=ua,
                locale=self._settings.locale,
                timezone_id=self._settings.timezone,
                permissions=["geolocation"],
                geolocation=self._settings.geolocation,
                color_scheme="light",
                device_scale_factor=1,
                has_touch=False,
                is_mobile=False,
                java_script_enabled=True,
            )

            logger.info("Browser context created with anti-detection settings")

            # Create initial page
            self._page = await self._context.new_page()

            # Inject stealth scripts
            await self._inject_stealth_scripts()

            logger.info("Browser initialization complete")

        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            await self.close()
            raise BrowserInitializationException(
                message=f"Browser initialization failed: {e}",
                error_type=type(e).__name__,
            ) from e

    async def _inject_stealth_scripts(self) -> None:
        """
        Inject JavaScript to hide automation indicators.

        This method adds various scripts to make the browser appear more
        like a real user's browser and less like an automated one.
        """
        if not self._page:
            return

        logger.debug("Injecting stealth scripts...")

        # Override navigator.webdriver
        await self._page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Mock plugins
        await self._page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        # Mock languages
        await self._page.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)

        # Chrome runtime
        await self._page.add_init_script("""
            window.chrome = {
                runtime: {}
            };
        """)

        # Mock permissions
        await self._page.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        # Override platform if needed
        await self._page.add_init_script("""
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
        """)

        logger.debug("Stealth scripts injected successfully")

    async def get_page(self) -> Page:
        """
        Get the current page instance.

        Returns:
            Current Playwright page.

        Raises:
            BrowserInitializationException: If browser not initialized.
        """
        if not self._page:
            raise BrowserInitializationException(
                "Browser not initialized. Call initialize() first."
            )
        return self._page

    async def new_page(self) -> Page:
        """
        Create a new page in the current context.

        Returns:
            New Playwright page.

        Raises:
            BrowserInitializationException: If browser not initialized.
        """
        if not self._context:
            raise BrowserInitializationException(
                "Browser context not initialized. Call initialize() first."
            )

        new_page = await self._context.new_page()
        await self._inject_stealth_scripts()

        logger.info("New page created")
        return new_page

    async def close_page(self, page: Optional[Page] = None) -> None:
        """
        Close a specific page or the current page.

        Args:
            page: Page to close. If None, closes current page.
        """
        page_to_close = page or self._page

        if page_to_close:
            await page_to_close.close()
            logger.info("Page closed")

            # If closing current page, set to None
            if page_to_close == self._page:
                self._page = None

    async def close(self) -> None:
        """Close all browser resources."""
        logger.info("Closing browser...")

        try:
            if self._context:
                await self._context.close()
                self._context = None

            if self._browser:
                await self._browser.close()
                self._browser = None

            if self._playwright:
                await self._playwright.stop()
                self._playwright = None

            self._page = None

            logger.info("Browser closed successfully")

        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    @property
    def is_initialized(self) -> bool:
        """Check if browser is initialized."""
        return self._browser is not None and self._context is not None

    @property
    def browser(self) -> Optional[Browser]:
        """Get the browser instance."""
        return self._browser

    @property
    def context(self) -> Optional[BrowserContext]:
        """Get the browser context."""
        return self._context

    @property
    def page(self) -> Optional[Page]:
        """Get the current page."""
        return self._page

    async def __aenter__(self) -> "BrowserManager":
        """Context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.close()

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (useful for testing).

        Warning:
            This should only be used in test environments.
        """
        if cls._instance:
            # Note: Browser should be closed before resetting
            cls._instance = None
            cls._initialized = False
            logger.debug("BrowserManager instance reset")
