"""
Feed page object for LinkedIn.

This module provides the FeedPage class for interacting with the LinkedIn feed.
"""

from playwright.async_api import Page

from src.config.constants import LINKEDIN_FEED_URL, URL_PATTERN_FEED
from src.config.settings import get_settings
from src.core.base_page import BasePage
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FeedPage(BasePage):
    """
    Page object for LinkedIn feed page.

    Handles operations on the main LinkedIn feed/home page.
    """

    def __init__(self, page: Page):
        """
        Initialize FeedPage.

        Args:
            page: Playwright page instance.
        """
        settings = get_settings()
        selectors = settings.get_selectors("feed_page")
        super().__init__(page, selectors)

    def get_url(self) -> str:
        """
        Get the feed page URL.

        Returns:
            LinkedIn feed URL.
        """
        return LINKEDIN_FEED_URL

    async def verify_loaded(self) -> bool:
        """
        Verify that the feed page is loaded.

        Returns:
            True if feed page is loaded, False otherwise.
        """
        try:
            # Check URL pattern
            current_url = await self.get_current_url()
            if URL_PATTERN_FEED not in current_url:
                logger.debug(f"Feed page not loaded - URL: {current_url}")
                return False

            # Check for nav bar element
            nav_bar_selector = self.get_selector("nav_bar")
            nav_present = await self.is_element_visible(nav_bar_selector, timeout=10000)

            logger.debug(f"Feed page loaded: {nav_present}")
            return nav_present

        except Exception as e:
            logger.error(f"Error verifying feed page: {e}")
            return False

    async def wait_for_feed_load(self, timeout: int = 30000) -> bool:
        """
        Wait for the feed to fully load.

        Args:
            timeout: Maximum wait time in milliseconds.

        Returns:
            True if feed loaded, False otherwise.
        """
        try:
            nav_bar_selector = self.get_selector("nav_bar")
            await self.wait_for_element(nav_bar_selector, timeout=timeout)
            logger.info("Feed page loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Feed failed to load: {e}")
            return False

    async def get_feed_posts_count(self) -> int:
        """
        Get the number of feed posts currently visible.

        Returns:
            Number of visible feed posts.
        """
        try:
            # This is a placeholder - actual selector would depend on LinkedIn's structure
            posts_selector = '[data-id*="urn:li:activity"]'
            count = await self.page.locator(posts_selector).count()
            logger.debug(f"Found {count} feed posts")
            return count

        except Exception as e:
            logger.error(f"Error counting feed posts: {e}")
            return 0

    async def scroll_feed(self, times: int = 3) -> None:
        """
        Scroll through the feed multiple times.

        Args:
            times: Number of times to scroll.
        """
        logger.info(f"Scrolling feed {times} times")

        for i in range(times):
            await self.scroll_randomly(min_amount=300, max_amount=600)
            logger.debug(f"Scroll {i+1}/{times} completed")

    async def perform_human_interaction(self) -> None:
        """Perform human-like interactions on the feed page."""
        logger.info("Performing human-like interactions on feed")

        # Random mouse movements
        await self.random_mouse_move()

        # Random scrolling
        await self.scroll_feed(times=2)

        logger.debug("Human interactions completed")
