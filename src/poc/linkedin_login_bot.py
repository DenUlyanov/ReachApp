#!/usr/bin/env python3
"""
LinkedIn Login Bot with Advanced Anti-Detection
Automates LinkedIn login with human-like behavior patterns
"""

import asyncio
import random
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import logging

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from dotenv import load_dotenv

# Configure logging with colorlog for better readability
try:
    import colorlog
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    logger = colorlog.getLogger(__name__)
    logger.addHandler(handler)
except ImportError:
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)


class LinkedInBot:
    """
    LinkedIn automation bot with comprehensive anti-detection measures
    """

    def __init__(self):
        """Initialize the LinkedIn bot with configuration from environment"""
        load_dotenv()

        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.sales_nav_url = os.getenv('SALES_NAVIGATOR_URL', 'https://www.linkedin.com/sales')
        self.headless = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'
        self.timeout = int(os.getenv('TIMEOUT', '30000'))
        self.max_attempts = int(os.getenv('MAX_LOGIN_ATTEMPTS', '3'))

        # Create necessary directories
        self.screenshot_dir = Path('../../screenshots')
        self.log_dir = Path('../../logs')
        self.screenshot_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

        # Setup file logging
        self._setup_file_logging()

        # State tracking
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def _setup_file_logging(self):
        """Configure file-based logging with rotation"""
        log_file = self.log_dir / f"linkedin_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {log_file}")

    async def human_delay(self, min_ms: int = 1000, max_ms: int = 8000):
        """
        Random delay to simulate human behavior

        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
        """
        delay = random.randint(min_ms, max_ms) / 1000.0
        logger.debug(f"Waiting {delay:.2f}s (human delay)")
        await asyncio.sleep(delay)

    async def human_type(self, element, text: str):
        """
        Type text with human-like delays between keystrokes

        Args:
            element: Playwright element to type into
            text: Text to type
        """
        logger.debug(f"Typing text with human-like delays")
        for char in text:
            await element.type(char, delay=random.randint(50, 150))

    async def random_mouse_movement(self):
        """Simulate random mouse movements on the page"""
        if not self.page:
            return

        try:
            # Get viewport size
            viewport = self.page.viewport_size
            if viewport:
                x = random.randint(100, viewport['width'] - 100)
                y = random.randint(100, viewport['height'] - 100)

                # Move mouse in a natural curve
                await self.page.mouse.move(x, y, steps=random.randint(5, 15))
                logger.debug(f"Mouse moved to ({x}, {y})")
        except Exception as e:
            logger.debug(f"Mouse movement error (non-critical): {e}")

    async def random_scroll(self):
        """Perform random scrolling behavior"""
        if not self.page:
            return

        try:
            scroll_amount = random.randint(100, 500)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            logger.debug(f"Scrolled {scroll_amount}px")
            await self.human_delay(500, 2000)
        except Exception as e:
            logger.debug(f"Scroll error (non-critical): {e}")

    async def take_screenshot(self, name: str):
        """
        Capture screenshot for debugging

        Args:
            name: Descriptive name for the screenshot
        """
        if not self.page:
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.screenshot_dir / f"{name}_{timestamp}.png"
        await self.page.screenshot(path=str(filename), full_page=True)
        logger.info(f"Screenshot saved: {filename}")

    async def detect_security_challenge(self) -> Tuple[bool, str]:
        """
        Detect various security challenges (CAPTCHA, 2FA, verification)

        Returns:
            Tuple of (detected, challenge_type)
        """
        if not self.page:
            return False, ""

        # Check for VISIBLE CAPTCHA challenges only
        captcha_selectors = [
            # Look for visible reCAPTCHA iframe (the actual challenge)
            'iframe[src*="recaptcha"][src*="bframe"]',  # reCAPTCHA challenge frame
            'iframe[title*="recaptcha"]',
            # Look for visible CAPTCHA containers
            '[id*="captcha"]:visible',
            '[class*="captcha"]:visible',
        ]

        for selector in captcha_selectors:
            count = await self.page.locator(selector).count()
            if count > 0:
                # Additional check: make sure it's actually visible
                try:
                    elements = await self.page.locator(selector).all()
                    for element in elements:
                        is_visible = await element.is_visible()
                        if is_visible:
                            logger.warning(f"Visible CAPTCHA detected! Selector: {selector}")
                            html = await element.evaluate("el => el.outerHTML")
                            logger.info(f"CAPTCHA element: {html[:200]}")
                            await self.take_screenshot("captcha_detected")
                            return True, "CAPTCHA"
                except Exception as e:
                    logger.error(f"Error checking element visibility: {e}")

        # Check for 2FA/verification - use more specific selectors
        verification_selectors = [
            # More specific patterns for 2FA
            'text=/enter.*verification.*code/i',  # "Enter verification code"
            'text=/enter.*security.*code/i',  # "Enter security code"
            'text=/two.*factor/i',  # "Two-factor authentication"
            'text=/6.*digit.*code/i',  # "6-digit code"
            'input[name*="verification"]',
            'input[name*="pin"]',
            'input[id*="verification"]',
            'input[id*="challenge"]',
            '[data-test-id*="verification"]',
            # LinkedIn-specific 2FA selectors
            'input[id="input__email_verification_pin"]',
            'input[id="input__phone_verification_pin"]',
        ]

        for selector in verification_selectors:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    # Verify it's actually visible
                    element = self.page.locator(selector).first
                    if await element.is_visible():
                        logger.warning(f"2FA/Verification challenge detected! Selector: {selector}")
                        await self.take_screenshot("verification_detected")
                        return True, "2FA/Verification"
            except Exception as e:
                # Selector might not support is_visible (like text selectors)
                # In that case, just check count
                if await self.page.locator(selector).count() > 0:
                    logger.warning(f"2FA/Verification challenge detected! Selector: {selector}")
                    await self.take_screenshot("verification_detected")
                    return True, "2FA/Verification"

        # Check for unusual activity warnings
        warning_selectors = [
            'text=/unusual.*activity/i',
            'text=/suspicious.*activity/i',
            'text=/temporarily.*restricted/i',
            'text=/account.*restricted/i',
        ]

        for selector in warning_selectors:
            if await self.page.locator(selector).count() > 0:
                logger.warning(f"Account warning detected! Selector: {selector}")
                await self.take_screenshot("account_warning")
                return True, "Account Warning"

        return False, ""

    async def setup_browser(self):
        """Initialize browser with anti-detection configurations"""
        logger.info("Setting up browser with anti-detection features...")

        playwright = await async_playwright().start()

        # Browser launch arguments for stealth
        launch_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
        ]

        # Add window size/maximized only for non-headless mode
        if not self.headless:
            launch_args.extend([
                '--start-maximized',
                '--window-position=0,0',
            ])

        # Launch browser
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=launch_args
        )

        # Create context with realistic settings
        # Use no_viewport for maximized window, or specific size for consistency
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080} if self.headless else None,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            color_scheme='light',
        )

        # Create page
        self.page = await self.context.new_page()

        # Inject anti-detection scripts
        await self._inject_stealth_scripts()

        logger.info("Browser setup complete")

    async def _inject_stealth_scripts(self):
        """Inject JavaScript to hide automation indicators"""
        if not self.page:
            return

        # Override navigator.webdriver
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Mock plugins
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        # Mock languages
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)

        # Chrome runtime
        await self.page.add_init_script("""
            window.chrome = {
                runtime: {}
            };
        """)

        logger.debug("Stealth scripts injected")

    async def login(self) -> bool:
        """
        Perform LinkedIn login with anti-detection measures

        Returns:
            bool: True if login successful, False otherwise
        """
        if not self.email or not self.password:
            logger.error("LinkedIn credentials not found in .env file")
            return False

        logger.info("Starting LinkedIn login process...")

        try:
            # Navigate to LinkedIn
            logger.info("Navigating to LinkedIn...")
            await self.page.goto('https://www.linkedin.com/login', wait_until='networkidle')
            await self.human_delay(2000, 4000)

            # Random mouse movement
            await self.random_mouse_movement()

            # Take initial screenshot
            await self.take_screenshot("01_login_page")

            # Check for security challenges before login
            detected, challenge_type = await self.detect_security_challenge()
            if detected:
                logger.error(f"Security challenge detected before login: {challenge_type}")
                return False

            # Fill email
            logger.info("Entering email...")
            email_input = self.page.locator('#username')
            await email_input.click()
            await self.human_delay(500, 1500)
            await self.human_type(email_input, self.email)
            await self.human_delay(1000, 2000)

            # Random mouse movement
            await self.random_mouse_movement()

            # Fill password
            logger.info("Entering password...")
            password_input = self.page.locator('#password')
            await password_input.click()
            await self.human_delay(500, 1500)
            await self.human_type(password_input, self.password)
            await self.human_delay(1000, 3000)

            # Take screenshot before submit
            await self.take_screenshot("02_credentials_entered")

            # Click login button
            logger.info("Clicking login button...")
            login_button = self.page.locator('button[type="submit"]')
            await login_button.click()

            # Wait for navigation
            await self.human_delay(3000, 5000)

            # Check for security challenges after login
            detected, challenge_type = await self.detect_security_challenge()
            if detected:
                logger.error(f"Security challenge detected: {challenge_type}")
                logger.info("Manual intervention may be required")
                await self.take_screenshot("03_security_challenge")

                # Wait for manual intervention if not headless
                if not self.headless:
                    logger.info("Please complete the challenge manually. Waiting 60 seconds...")
                    await asyncio.sleep(60)

                return False

            # Verify login success
            await self.page.wait_for_load_state('domcontentloaded', timeout=self.timeout)

            # Check if we're on the feed page (successful login)
            if 'feed' in self.page.url or 'mynetwork' in self.page.url:
                logger.info("Login successful!")
                await self.take_screenshot("03_login_success")
                return True
            else:
                logger.error(f"Login may have failed. Current URL: {self.page.url}")
                await self.take_screenshot("03_login_failed")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            await self.take_screenshot("error_login")
            return False


    async def run(self):
        """Main execution flow"""
        logger.info("=== LinkedIn Login Bot Starting ===")
        logger.info(f"Headless mode: {self.headless}")
        logger.info(f"Max login attempts: {self.max_attempts}")

        try:
            # Setup browser
            await self.setup_browser()

            # Attempt login with retries
            login_success = False
            for attempt in range(1, self.max_attempts + 1):
                logger.info(f"Login attempt {attempt}/{self.max_attempts}")

                login_success = await self.login()

                if login_success:
                    break
                else:
                    if attempt < self.max_attempts:
                        logger.warning(f"Login failed, retrying in 10 seconds...")
                        await asyncio.sleep(10)

            if not login_success:
                logger.error("All login attempts failed")
                return

            # Post-login activities
            logger.info("Performing post-login activities...")

            # Random scroll on feed
            await self.random_scroll()
            await self.human_delay(2000, 4000)

            # Navigate to Sales Navigator (if configured)
            # TODO

            # Keep browser open for inspection if not headless
            if not self.headless:
                logger.info("Browser will remain open for inspection...")
                logger.info("Press Ctrl+C to close")
                try:
                    await asyncio.sleep(300)  # Keep open for 5 minutes
                except KeyboardInterrupt:
                    logger.info("Interrupted by user")

        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            await self.take_screenshot("error_fatal")

        finally:
            await self.cleanup()

    async def cleanup(self):
        """Clean up browser resources"""
        logger.info("Cleaning up...")

        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

        logger.info("=== LinkedIn Login Bot Finished ===")


async def main():
    """Entry point"""
    bot = LinkedInBot()
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
