"""
Abstract base page class for Page Object Model.

This module provides the foundational BasePage class that all page objects
inherit from, implementing common page operations and patterns.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from src.config.constants import DEFAULT_ACTION_TIMEOUT, DEFAULT_TIMEOUT
from src.exceptions import ElementNotFoundException, TimeoutException
from src.utils.helpers import (
    human_type,
    random_delay,
    random_mouse_move,
    random_scroll,
    safe_click,
)
from src.utils.logger import get_logger
from src.utils.screenshot_manager import get_screenshot_manager

logger = get_logger(__name__)


class BasePage(ABC):
    """
    Abstract base class for all page objects.

    This class provides common functionality for interacting with web pages,
    including element operations, navigation, and human-like behavior simulation.

    Attributes:
        page: Playwright page instance.
        selectors: Dictionary of CSS selectors for the page.
        screenshot_manager: Screenshot manager for capturing page states.
    """

    def __init__(self, page: Page, selectors: dict[str, str]):
        """
        Initialize BasePage.

        Args:
            page: Playwright page instance.
            selectors: Dictionary mapping logical names to CSS selectors.
        """
        self.page = page
        self.selectors = selectors
        self.screenshot_manager = get_screenshot_manager()
        logger.debug(f"{self.__class__.__name__} initialized")

    @abstractmethod
    async def verify_loaded(self) -> bool:
        """
        Verify that the page is fully loaded.

        This method should be implemented by each page object to check
        for page-specific elements or conditions.

        Returns:
            True if page is loaded, False otherwise.
        """
        pass

    @abstractmethod
    def get_url(self) -> str:
        """
        Get the expected URL for this page.

        Returns:
            URL string or URL pattern for the page.
        """
        pass

    async def navigate(self, url: Optional[str] = None) -> None:
        """
        Navigate to the page URL.

        Args:
            url: Optional URL to navigate to. If not provided, uses get_url().

        Raises:
            TimeoutException: If navigation times out.
        """
        target_url = url or self.get_url()

        try:
            logger.info(f"Navigating to: {target_url}")
            await self.page.goto(target_url, wait_until="networkidle")
            await random_delay(2000, 4000)
            logger.info(f"Navigation complete: {self.page.url}")

        except PlaywrightTimeoutError as e:
            logger.error(f"Navigation timeout: {target_url}")
            raise TimeoutException(
                message=f"Navigation timed out for {target_url}",
                timeout=DEFAULT_TIMEOUT / 1000,
                operation="navigate",
            ) from e

    async def wait_for_element(
        self,
        selector: str,
        timeout: int = DEFAULT_TIMEOUT,
        state: str = "visible",
    ) -> None:
        """
        Wait for an element to reach a specific state.

        Args:
            selector: CSS selector for the element.
            timeout: Timeout in milliseconds.
            state: Element state ('visible', 'attached', 'detached', 'hidden').

        Raises:
            TimeoutException: If element doesn't reach desired state in time.
        """
        try:
            logger.debug(f"Waiting for element: {selector} (state={state})")
            await self.page.locator(selector).wait_for(
                state=state, timeout=timeout
            )
            logger.debug(f"Element found: {selector}")

        except PlaywrightTimeoutError as e:
            logger.error(f"Element not found: {selector}")
            raise TimeoutException(
                message=f"Element not found: {selector}",
                timeout=timeout / 1000,
                operation="wait_for_element",
                selector=selector,
            ) from e

    async def click_element(
        self,
        selector: str,
        timeout: int = DEFAULT_ACTION_TIMEOUT,
        human_like: bool = True,
    ) -> None:
        """
        Click an element with optional human-like behavior.

        Args:
            selector: CSS selector for the element.
            timeout: Timeout in milliseconds.
            human_like: Whether to add human-like delays and movements.

        Raises:
            ElementNotFoundException: If element not found.
        """
        try:
            logger.debug(f"Clicking element: {selector}")

            if human_like:
                await random_delay(500, 1500)
                await random_mouse_move(self.page)

            element = self.page.locator(selector)
            await element.wait_for(state="visible", timeout=timeout)
            await element.click()

            if human_like:
                await random_delay(1000, 2000)

            logger.debug(f"Clicked: {selector}")

        except PlaywrightTimeoutError as e:
            logger.error(f"Failed to click element: {selector}")
            raise ElementNotFoundException(
                message=f"Element not found for clicking: {selector}",
                selector=selector,
            ) from e

    async def type_text(
        self,
        selector: str,
        text: str,
        human_like: bool = True,
        clear_first: bool = True,
    ) -> None:
        """
        Type text into an element.

        Args:
            selector: CSS selector for the element.
            text: Text to type.
            human_like: Whether to simulate human-like typing.
            clear_first: Whether to clear existing text first.

        Raises:
            ElementNotFoundException: If element not found.
        """
        try:
            logger.debug(f"Typing into element: {selector}")

            element = self.page.locator(selector)
            await element.wait_for(state="visible")

            # Clear existing text if requested
            if clear_first:
                await element.fill("")

            # Type with human-like delays if requested
            if human_like:
                await human_type(self.page, selector, text)
            else:
                await element.type(text)

            logger.debug(f"Text entered into: {selector}")

        except PlaywrightTimeoutError as e:
            logger.error(f"Failed to type into element: {selector}")
            raise ElementNotFoundException(
                message=f"Element not found for typing: {selector}",
                selector=selector,
            ) from e

    async def get_text(
        self,
        selector: str,
        timeout: int = DEFAULT_ACTION_TIMEOUT,
    ) -> str:
        """
        Get text content from an element.

        Args:
            selector: CSS selector for the element.
            timeout: Timeout in milliseconds.

        Returns:
            Text content of the element.

        Raises:
            ElementNotFoundException: If element not found.
        """
        try:
            element = self.page.locator(selector).first
            await element.wait_for(state="visible", timeout=timeout)
            text = await element.text_content() or ""
            return text.strip()

        except PlaywrightTimeoutError as e:
            logger.error(f"Failed to get text from element: {selector}")
            raise ElementNotFoundException(
                message=f"Element not found for text extraction: {selector}",
                selector=selector,
            ) from e

    async def get_attribute(
        self,
        selector: str,
        attribute: str,
        timeout: int = DEFAULT_ACTION_TIMEOUT,
    ) -> Optional[str]:
        """
        Get an attribute value from an element.

        Args:
            selector: CSS selector for the element.
            attribute: Attribute name.
            timeout: Timeout in milliseconds.

        Returns:
            Attribute value or None if not found.

        Raises:
            ElementNotFoundException: If element not found.
        """
        try:
            element = self.page.locator(selector).first
            await element.wait_for(state="attached", timeout=timeout)
            return await element.get_attribute(attribute)

        except PlaywrightTimeoutError as e:
            logger.error(f"Failed to get attribute from element: {selector}")
            raise ElementNotFoundException(
                message=f"Element not found for attribute extraction: {selector}",
                selector=selector,
            ) from e

    async def is_element_visible(
        self,
        selector: str,
        timeout: int = 5000,
    ) -> bool:
        """
        Check if an element is visible.

        Args:
            selector: CSS selector for the element.
            timeout: Timeout in milliseconds.

        Returns:
            True if element is visible, False otherwise.
        """
        try:
            element = self.page.locator(selector).first
            await element.wait_for(state="visible", timeout=timeout)
            return await element.is_visible()
        except Exception:
            return False

    async def is_element_present(self, selector: str) -> bool:
        """
        Check if an element is present in the DOM.

        Args:
            selector: CSS selector for the element.

        Returns:
            True if element exists, False otherwise.
        """
        count = await self.page.locator(selector).count()
        return count > 0

    async def wait_for_url_pattern(
        self,
        pattern: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bool:
        """
        Wait for URL to match a pattern.

        Args:
            pattern: String pattern to match in URL.
            timeout: Timeout in milliseconds.

        Returns:
            True if URL matches pattern within timeout, False otherwise.
        """
        try:
            await self.page.wait_for_url(
                f"**/*{pattern}*", timeout=timeout
            )
            logger.debug(f"URL pattern matched: {pattern}")
            return True
        except PlaywrightTimeoutError:
            logger.warning(f"URL pattern not matched: {pattern}")
            return False

    async def take_screenshot(
        self,
        name: str,
        full_page: bool = True,
    ) -> Optional[Any]:
        """
        Capture a screenshot of the page.

        Args:
            name: Descriptive name for the screenshot.
            full_page: Whether to capture full page or just viewport.

        Returns:
            Path to the screenshot file.
        """
        return await self.screenshot_manager.capture(
            self.page, name, full_page=full_page
        )

    async def scroll_randomly(
        self,
        min_amount: int = 100,
        max_amount: int = 500,
    ) -> None:
        """
        Perform random scrolling behavior.

        Args:
            min_amount: Minimum scroll amount in pixels.
            max_amount: Maximum scroll amount in pixels.
        """
        await random_scroll(self.page, min_amount, max_amount)

    async def random_mouse_move(self) -> None:
        """Perform random mouse movements."""
        await random_mouse_move(self.page)

    async def get_current_url(self) -> str:
        """
        Get the current page URL.

        Returns:
            Current URL string.
        """
        return self.page.url

    async def reload_page(self) -> None:
        """Reload the current page."""
        logger.info("Reloading page")
        await self.page.reload()
        await random_delay(2000, 4000)

    async def go_back(self) -> None:
        """Navigate back in browser history."""
        logger.info("Navigating back")
        await self.page.go_back()
        await random_delay(1000, 2000)

    async def go_forward(self) -> None:
        """Navigate forward in browser history."""
        logger.info("Navigating forward")
        await self.page.go_forward()
        await random_delay(1000, 2000)

    def get_selector(self, name: str) -> str:
        """
        Get a selector by its logical name.

        Args:
            name: Logical name of the selector.

        Returns:
            CSS selector string.

        Raises:
            KeyError: If selector name not found.
        """
        if name not in self.selectors:
            raise KeyError(f"Selector '{name}' not found in {self.__class__.__name__}")
        return self.selectors[name]
