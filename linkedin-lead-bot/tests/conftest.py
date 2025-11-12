"""
Pytest configuration and fixtures for LinkedIn Bot tests.

This module provides shared fixtures and configuration for all test modules.
"""

import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

# Add parent directory to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bot.linkedin_bot import LinkedInBot
from src.config.settings import Settings, get_settings
from src.core.browser_manager import BrowserManager


# ============================================================================
# Session-level fixtures
# ============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an event loop for the test session.

    Yields:
        Event loop instance.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """
    Get settings for testing.

    Returns:
        Settings instance with test configuration.
    """
    # Set testing flag
    os.environ["TESTING"] = "true"

    # Get settings
    settings = get_settings()

    return settings


# ============================================================================
# Browser-related fixtures
# ============================================================================


@pytest.fixture(scope="session")
async def browser_manager(
    test_settings: Settings,
) -> AsyncGenerator[BrowserManager, None]:
    """
    Create a browser manager for testing.

    Args:
        test_settings: Test settings.

    Yields:
        BrowserManager instance.
    """
    manager = await BrowserManager.get_instance()
    await manager.initialize(headless=True, slow_mo=0)
    yield manager
    await manager.close()
    BrowserManager.reset_instance()


@pytest.fixture(scope="function")
async def browser() -> AsyncGenerator[Browser, None]:
    """
    Create a Playwright browser instance for testing.

    Yields:
        Browser instance.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture(scope="function")
async def context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """
    Create a browser context for testing.

    Args:
        browser: Browser instance.

    Yields:
        BrowserContext instance.
    """
    context = await browser.new_context()
    yield context
    await context.close()


@pytest.fixture(scope="function")
async def page(context: BrowserContext) -> AsyncGenerator[Page, None]:
    """
    Create a page for testing.

    Args:
        context: Browser context.

    Yields:
        Page instance.
    """
    page = await context.new_page()
    yield page
    await page.close()


# ============================================================================
# Mock fixtures
# ============================================================================


@pytest.fixture
def mock_page() -> Mock:
    """
    Create a mock Playwright page for unit testing.

    Returns:
        Mock page instance.
    """
    page = AsyncMock(spec=Page)
    page.url = "https://www.linkedin.com/feed"
    page.viewport_size = {"width": 1920, "height": 1080}
    page.locator = Mock()
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.screenshot = AsyncMock()
    page.evaluate = AsyncMock()
    page.mouse = Mock()
    page.mouse.move = AsyncMock()

    # Mock locator
    mock_locator = AsyncMock()
    mock_locator.count = AsyncMock(return_value=1)
    mock_locator.first = AsyncMock()
    mock_locator.all = AsyncMock(return_value=[])
    mock_locator.wait_for = AsyncMock()
    mock_locator.click = AsyncMock()
    mock_locator.type = AsyncMock()
    mock_locator.fill = AsyncMock()
    mock_locator.is_visible = AsyncMock(return_value=True)
    mock_locator.text_content = AsyncMock(return_value="Test content")

    page.locator.return_value = mock_locator

    return page


@pytest.fixture
def mock_browser_manager() -> Mock:
    """
    Create a mock BrowserManager for testing.

    Returns:
        Mock BrowserManager instance.
    """
    manager = AsyncMock(spec=BrowserManager)
    manager.is_initialized = True
    manager.initialize = AsyncMock()
    manager.get_page = AsyncMock()
    manager.close = AsyncMock()

    # Mock page
    mock_page_instance = AsyncMock()
    mock_page_instance.url = "https://www.linkedin.com/feed"
    manager.get_page.return_value = mock_page_instance

    return manager


@pytest.fixture
def mock_settings() -> Settings:
    """
    Create mock settings for testing.

    Returns:
        Settings instance with test data.
    """
    os.environ["TESTING"] = "true"
    os.environ["LINKEDIN_EMAIL"] = "test@example.com"
    os.environ["LINKEDIN_PASSWORD"] = "test_password"

    settings = Settings()
    return settings


# ============================================================================
# Bot-related fixtures
# ============================================================================


@pytest.fixture
async def bot_instance(
    test_settings: Settings,
) -> AsyncGenerator[LinkedInBot, None]:
    """
    Create a LinkedInBot instance for testing.

    Args:
        test_settings: Test settings.

    Yields:
        LinkedInBot instance.
    """
    bot = LinkedInBot(settings=test_settings)
    # Note: Don't initialize browser by default to avoid overhead
    yield bot
    # Cleanup if browser was initialized
    if bot.browser_manager and bot.browser_manager.is_initialized:
        await bot.cleanup()


@pytest.fixture
async def initialized_bot(
    bot_instance: LinkedInBot,
) -> AsyncGenerator[LinkedInBot, None]:
    """
    Create and initialize a LinkedInBot instance.

    Args:
        bot_instance: Bot instance.

    Yields:
        Initialized LinkedInBot instance.
    """
    await bot_instance.initialize(headless=True, slow_mo=0)
    yield bot_instance
    await bot_instance.cleanup()


# ============================================================================
# Test data fixtures
# ============================================================================


@pytest.fixture
def test_credentials() -> dict[str, str]:
    """
    Provide test credentials.

    Returns:
        Dictionary with test credentials.
    """
    return {
        "email": "test@example.com",
        "password": "test_password_123",
    }


@pytest.fixture
def test_selectors() -> dict[str, str]:
    """
    Provide test selectors.

    Returns:
        Dictionary with test selectors.
    """
    return {
        "email_input": "#username",
        "password_input": "#password",
        "sign_in_button": 'button[type="submit"]',
        "nav_bar": "nav.global-nav",
    }


# ============================================================================
# Cleanup fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_env():
    """
    Clean up environment variables after each test.

    Yields:
        None
    """
    yield
    # Reset testing flag
    if "TESTING" in os.environ:
        os.environ.pop("TESTING", None)


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Reset singleton instances after each test.

    Yields:
        None
    """
    yield
    # Reset BrowserManager singleton (only if safe)
    # This is handled by individual tests that use browser_manager


# ============================================================================
# Markers
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "requires_credentials: mark test as requiring credentials"
    )
    config.addinivalue_line(
        "markers", "requires_browser: mark test as requiring browser"
    )


# ============================================================================
# Collection hooks
# ============================================================================


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically.

    Args:
        config: Pytest config.
        items: Collected test items.
    """
    for item in items:
        # Add markers based on test location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)
