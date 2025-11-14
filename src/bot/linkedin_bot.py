"""
Main LinkedIn Bot orchestrator.

This module provides the LinkedInBot class that coordinates all bot operations,
managing the browser, pages, and workflow execution.
"""

from typing import Optional

from src.config.settings import Settings, get_settings
from src.core.browser_manager import BrowserManager
from src.exceptions import (
    BrowserInitializationException,
    CaptchaDetectedException,
    ConfigurationException,
    LoginFailedException,
    TwoFactorRequiredException,
    UnusualActivityException,
)
from src.pages.feed_page import FeedPage
from src.pages.login_page import LoginPage
from src.pages.sales_navigator_page import SalesNavigatorPage
from src.utils.helpers import random_delay
from src.utils.logger import get_logger
from src.utils.screenshot_manager import get_screenshot_manager

logger = get_logger(__name__)


class LinkedInBot:
    """
    Main orchestrator for LinkedIn automation.

    This class manages the bot's lifecycle, coordinating browser management,
    page navigation, and execution of automation tasks.

    Attributes:
        settings: Configuration settings.
        browser_manager: Singleton browser manager instance.
        screenshot_manager: Screenshot manager instance.
        login_page: Login page object.
        feed_page: Feed page object.
        sales_nav_page: Sales Navigator page object.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the LinkedIn Bot.

        Args:
            settings: Optional Settings instance. If not provided, uses default.
        """
        self.settings = settings or get_settings()
        self.browser_manager: Optional[BrowserManager] = None
        self.screenshot_manager = get_screenshot_manager()

        # Page objects (initialized after browser setup)
        self.login_page: Optional[LoginPage] = None
        self.feed_page: Optional[FeedPage] = None
        self.sales_nav_page: Optional[SalesNavigatorPage] = None

        logger.info("LinkedInBot instance created")

    async def initialize(
        self,
        headless: Optional[bool] = None,
        slow_mo: Optional[int] = None,
    ) -> None:
        """
        Initialize the bot and browser.

        Args:
            headless: Override headless mode setting.
            slow_mo: Override slow motion setting.

        Raises:
            BrowserInitializationException: If browser initialization fails.
        """
        logger.info("Initializing LinkedIn Bot...")

        try:
            # Create session directory for screenshots
            self.screenshot_manager.create_session_directory()

            # Initialize browser
            self.browser_manager = await BrowserManager.get_instance()
            await self.browser_manager.initialize(
                headless=headless,
                slow_mo=slow_mo,
            )

            # Initialize page objects
            page = await self.browser_manager.get_page()
            self.login_page = LoginPage(page)
            self.feed_page = FeedPage(page)
            self.sales_nav_page = SalesNavigatorPage(page)

            logger.info("LinkedIn Bot initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            await self.cleanup()
            raise BrowserInitializationException(
                message=f"Bot initialization failed: {e}",
                error_type=type(e).__name__,
            ) from e

    async def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        handle_challenges: bool = True,
    ) -> bool:
        """
        Perform LinkedIn login.

        Args:
            email: LinkedIn email (uses settings if not provided).
            password: LinkedIn password (uses settings if not provided).
            handle_challenges: Whether to handle security challenges.

        Returns:
            True if login successful, False otherwise.

        Raises:
            ConfigurationException: If credentials not provided.
            LoginFailedException: If login fails.
            CaptchaDetectedException: If CAPTCHA challenge detected.
            TwoFactorRequiredException: If 2FA required.
            UnusualActivityException: If unusual activity detected.
        """
        if not self.login_page:
            raise BrowserInitializationException("Bot not initialized")

        # Use provided credentials or fall back to settings
        login_email = email or self.settings.linkedin_email
        login_password = password or self.settings.linkedin_password

        # Validate credentials
        if not login_email or not login_password:
            raise ConfigurationException(
                message="LinkedIn credentials not configured",
                config_key="credentials",
            )

        logger.info(f"Logging in with email: {login_email[:3]}***")

        try:
            # Perform login
            success = await self.login_page.login(
                email=login_email,
                password=login_password,
                handle_challenges=handle_challenges,
                wait_time_on_challenge=60 if not self.settings.headless else 0,
            )

            return success

        except (
            CaptchaDetectedException,
            TwoFactorRequiredException,
            UnusualActivityException,
        ) as e:
            logger.error(f"Security challenge during login: {e}")
            raise

        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise LoginFailedException(
                message=f"Login failed: {e}",
                error_type=type(e).__name__,
            ) from e

    async def navigate_to_feed(self) -> bool:
        """
        Navigate to LinkedIn feed.

        Returns:
            True if navigation successful, False otherwise.
        """
        if not self.feed_page:
            raise BrowserInitializationException("Bot not initialized")

        try:
            logger.info("Navigating to LinkedIn feed")
            await self.feed_page.navigate()
            success = await self.feed_page.wait_for_feed_load()

            if success:
                logger.info("Successfully navigated to feed")

            return success

        except Exception as e:
            logger.error(f"Failed to navigate to feed: {e}")
            return False

    async def navigate_to_sales_navigator(self) -> bool:
        """
        Navigate to Sales Navigator.

        Returns:
            True if navigation successful, False otherwise.
        """
        if not self.sales_nav_page:
            raise BrowserInitializationException("Bot not initialized")

        try:
            logger.info("Navigating to Sales Navigator")
            await self.sales_nav_page.navigate()
            success = await self.sales_nav_page.wait_for_sales_nav_load()

            if success:
                logger.info("Successfully navigated to Sales Navigator")
                await self.sales_nav_page.take_screenshot("sales_navigator_loaded")

            return success

        except Exception as e:
            logger.error(f"Failed to navigate to Sales Navigator: {e}")
            await self.sales_nav_page.take_screenshot("sales_nav_error")
            return False

    async def perform_feed_interaction(self, scroll_times: int = 3) -> None:
        """
        Perform human-like interactions on the feed.

        Args:
            scroll_times: Number of times to scroll through feed.
        """
        if not self.feed_page:
            raise BrowserInitializationException("Bot not initialized")

        logger.info("Performing feed interactions")
        await self.feed_page.perform_human_interaction()
        await self.feed_page.scroll_feed(times=scroll_times)

    async def run_health_check(self) -> dict[str, any]:
        """
        Run a comprehensive health check.

        Returns:
            Dictionary with health check results.
        """
        logger.info("Running health check...")

        health = {
            "browser_initialized": False,
            "login_accessible": False,
            "feed_accessible": False,
            "sales_nav_accessible": False,
            "credentials_configured": False,
        }

        try:
            # Check browser
            health["browser_initialized"] = (
                self.browser_manager and self.browser_manager.is_initialized
            )

            # Check credentials
            health["credentials_configured"] = bool(
                self.settings.linkedin_email and self.settings.linkedin_password
            )

            # Check login page
            if self.login_page:
                await self.login_page.navigate()
                health["login_accessible"] = await self.login_page.verify_loaded()

            # Check feed (requires login)
            if health["credentials_configured"]:
                try:
                    await self.login()
                    health["feed_accessible"] = await self.feed_page.verify_loaded()

                    # Check Sales Navigator
                    sales_nav_health = await self.sales_nav_page.perform_health_check()
                    health["sales_nav_accessible"] = sales_nav_health.get(
                        "accessible", False
                    )
                    health["sales_nav_details"] = sales_nav_health

                except Exception as e:
                    logger.warning(f"Login failed during health check: {e}")

            logger.info(f"Health check complete: {health}")
            return health

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health["error"] = str(e)
            return health

    async def cleanup(self) -> None:
        """Clean up bot resources."""
        logger.info("Cleaning up bot resources...")

        try:
            if self.browser_manager:
                await self.browser_manager.close()

            logger.info("Bot cleanup complete")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    async def __aenter__(self) -> "LinkedInBot":
        """Context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.cleanup()

    async def run_demo_workflow(self) -> None:
        """
        Run a demo workflow (login -> feed -> sales nav).

        This is a demonstration of the bot's capabilities.
        """
        logger.info("🤖 Starting demo workflow...")

        try:
            # Step 1: Login
            logger.info("Step 1: Logging in to LinkedIn")
            await self.login()
            await random_delay(2000, 4000)

            # Step 2: Interact with feed
            logger.info("Step 2: Interacting with feed")
            await self.perform_feed_interaction(scroll_times=2)
            await random_delay(2000, 4000)

            # Step 3: Navigate to Sales Navigator
            logger.info("Step 3: Navigating to Sales Navigator")
            success = await self.navigate_to_sales_navigator()

            if success:
                logger.info("✅ Demo workflow completed successfully!")
            else:
                logger.warning("⚠️ Demo workflow completed with warnings")

            # Keep browser open if not headless
            if not self.settings.headless:
                logger.info("Browser will remain open for inspection (60s)...")
                await random_delay(60000, 60000)

        except Exception as e:
            logger.error(f"❌ Demo workflow failed: {e}")
            raise
