"""
Helper utilities for human-like behavior simulation.

This module provides functions to simulate human behavior patterns
such as random delays, typing, mouse movements, and scrolling.
"""

import asyncio
import random
from functools import wraps
from time import time
from typing import Any, Callable, Coroutine, TypeVar

from playwright.async_api import Page

from src.config.constants import (
    MAX_ACTION_DELAY,
    MAX_MOUSE_STEPS,
    MAX_SCROLL_DELAY,
    MAX_TYPING_DELAY,
    MIN_ACTION_DELAY,
    MIN_MOUSE_STEPS,
    MIN_SCROLL_DELAY,
    MIN_TYPING_DELAY,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


async def random_delay(
    min_ms: int = MIN_ACTION_DELAY,
    max_ms: int = MAX_ACTION_DELAY,
) -> None:
    """
    Introduce a random delay to simulate human thinking/reaction time.

    Args:
        min_ms: Minimum delay in milliseconds.
        max_ms: Maximum delay in milliseconds.
    """
    delay_ms = random.randint(min_ms, max_ms)
    delay_sec = delay_ms / 1000.0
    logger.debug(f"Random delay: {delay_sec:.2f}s")
    await asyncio.sleep(delay_sec)


async def human_type(
    page: Page,
    selector: str,
    text: str,
    min_delay: int = MIN_TYPING_DELAY,
    max_delay: int = MAX_TYPING_DELAY,
) -> None:
    """
    Type text with human-like delays between keystrokes.

    Args:
        page: Playwright page instance.
        selector: Element selector to type into.
        text: Text to type.
        min_delay: Minimum delay between keystrokes in milliseconds.
        max_delay: Maximum delay between keystrokes in milliseconds.
    """
    logger.debug(f"Typing into {selector} with human-like delays")

    element = page.locator(selector)

    for char in text:
        delay = random.randint(min_delay, max_delay)
        await element.type(char, delay=delay)


async def random_mouse_move(
    page: Page,
    min_steps: int = MIN_MOUSE_STEPS,
    max_steps: int = MAX_MOUSE_STEPS,
) -> None:
    """
    Perform random mouse movements to simulate human behavior.

    Args:
        page: Playwright page instance.
        min_steps: Minimum number of movement steps.
        max_steps: Maximum number of movement steps.
    """
    try:
        viewport = page.viewport_size
        if not viewport:
            logger.debug("No viewport size available, skipping mouse movement")
            return

        # Generate random target position (avoid edges)
        x = random.randint(100, viewport["width"] - 100)
        y = random.randint(100, viewport["height"] - 100)

        # Move with random number of steps for natural curve
        steps = random.randint(min_steps, max_steps)

        await page.mouse.move(x, y, steps=steps)
        logger.debug(f"Mouse moved to ({x}, {y}) in {steps} steps")

    except Exception as e:
        logger.debug(f"Mouse movement error (non-critical): {e}")


async def random_scroll(
    page: Page,
    min_amount: int = 100,
    max_amount: int = 500,
    direction: str = "down",
) -> None:
    """
    Perform random scrolling to simulate human browsing.

    Args:
        page: Playwright page instance.
        min_amount: Minimum scroll amount in pixels.
        max_amount: Maximum scroll amount in pixels.
        direction: Scroll direction ('down' or 'up').
    """
    try:
        scroll_amount = random.randint(min_amount, max_amount)

        # Negative for up, positive for down
        scroll_value = scroll_amount if direction == "down" else -scroll_amount

        await page.evaluate(f"window.scrollBy(0, {scroll_value})")
        logger.debug(f"Scrolled {direction} by {scroll_amount}px")

        # Small delay after scrolling
        await random_delay(MIN_SCROLL_DELAY, MAX_SCROLL_DELAY)

    except Exception as e:
        logger.debug(f"Scroll error (non-critical): {e}")


async def smooth_scroll_to_element(
    page: Page,
    selector: str,
    offset: int = 100,
) -> None:
    """
    Smoothly scroll to an element with human-like behavior.

    Args:
        page: Playwright page instance.
        selector: Element selector to scroll to.
        offset: Offset from the element in pixels (default centers it).
    """
    try:
        element = page.locator(selector).first

        # Scroll element into view with smooth behavior
        await element.evaluate(
            """(element, offset) => {
                const y = element.getBoundingClientRect().top + window.pageYOffset - offset;
                window.scrollTo({ top: y, behavior: 'smooth' });
            }""",
            offset,
        )

        logger.debug(f"Smoothly scrolled to element: {selector}")
        await random_delay(500, 1500)

    except Exception as e:
        logger.debug(f"Smooth scroll error: {e}")


async def random_page_interaction(page: Page) -> None:
    """
    Perform a random page interaction (scroll or mouse move).

    Args:
        page: Playwright page instance.
    """
    actions = [
        lambda: random_mouse_move(page),
        lambda: random_scroll(page),
    ]

    action = random.choice(actions)
    await action()


def retry_on_exception(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    backoff: float = 2.0,
) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]]:
    """
    Decorator to retry an async function on exception.

    Args:
        max_attempts: Maximum number of retry attempts.
        delay: Initial delay between retries in seconds.
        exceptions: Tuple of exception types to catch.
        backoff: Multiplier for delay between retries.

    Returns:
        Decorated function with retry logic.

    Example:
        ```python
        @retry_on_exception(max_attempts=3, delay=2.0)
        async def flaky_operation():
            # Your code here
            pass
        ```
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            # This should never be reached, but satisfies type checker
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected error in retry logic")

        return wrapper

    return decorator


def timing_decorator(
    log_result: bool = True,
) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]]:
    """
    Decorator to measure execution time of async functions.

    Args:
        log_result: Whether to log the execution time.

    Returns:
        Decorated function with timing measurement.

    Example:
        ```python
        @timing_decorator()
        async def slow_operation():
            # Your code here
            pass
        ```
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                elapsed = time() - start_time
                if log_result:
                    logger.debug(
                        f"{func.__name__} executed in {elapsed:.2f}s"
                    )

        return wrapper

    return decorator


def generate_realistic_viewport() -> dict[str, int]:
    """
    Generate a realistic viewport size.

    Returns:
        Dictionary with width and height.
    """
    common_resolutions = [
        {"width": 1920, "height": 1080},  # Full HD
        {"width": 1366, "height": 768},  # Common laptop
        {"width": 1536, "height": 864},  # Common laptop
        {"width": 1440, "height": 900},  # MacBook
        {"width": 2560, "height": 1440},  # QHD
    ]

    return random.choice(common_resolutions)


def generate_random_user_agent() -> str:
    """
    Generate a random but realistic user agent string.

    Returns:
        User agent string.
    """
    chrome_versions = ["130.0.0.0", "131.0.0.0", "132.0.0.0"]
    chrome_version = random.choice(chrome_versions)

    return (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_version} Safari/537.36"
    )


async def wait_for_network_idle(
    page: Page,
    timeout: int = 30000,
    idle_time: int = 500,
) -> None:
    """
    Wait for network to be idle (no requests for specified time).

    Args:
        page: Playwright page instance.
        timeout: Maximum wait time in milliseconds.
        idle_time: Time in milliseconds to consider network idle.
    """
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout)
        logger.debug("Network is idle")
    except Exception as e:
        logger.debug(f"Network idle wait failed: {e}")


async def safe_click(
    page: Page,
    selector: str,
    timeout: int = 30000,
    delay_before: tuple[int, int] = (500, 1500),
    delay_after: tuple[int, int] = (1000, 2000),
) -> bool:
    """
    Safely click an element with delays and error handling.

    Args:
        page: Playwright page instance.
        selector: Element selector.
        timeout: Timeout in milliseconds.
        delay_before: (min, max) delay before click in milliseconds.
        delay_after: (min, max) delay after click in milliseconds.

    Returns:
        True if click successful, False otherwise.
    """
    try:
        # Wait for element
        element = page.locator(selector)
        await element.wait_for(state="visible", timeout=timeout)

        # Human delay before click
        await random_delay(*delay_before)

        # Click
        await element.click()
        logger.debug(f"Clicked element: {selector}")

        # Human delay after click
        await random_delay(*delay_after)

        return True

    except Exception as e:
        logger.error(f"Failed to click element {selector}: {e}")
        return False
