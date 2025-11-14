"""
Login page object for LinkedIn.

This module provides the LoginPage class for handling LinkedIn login operations
with security challenge detection and human-like behavior.
"""

from typing import Optional, Tuple

from playwright.async_api import Page

from src.config.constants import (
    CAPTCHA_SELECTORS,
    CHALLENGE_TYPE_2FA,
    CHALLENGE_TYPE_CAPTCHA,
    CHALLENGE_TYPE_UNUSUAL_ACTIVITY,
    CHALLENGE_TYPE_VERIFICATION,
    LINKEDIN_LOGIN_URL,
    URL_PATTERN_FEED,
    URL_PATTERN_MY_NETWORK,
    VERIFICATION_SELECTORS,
    WARNING_SELECTORS,
)
from src.config.settings import get_settings
from src.core.base_page import BasePage
from src.exceptions import (
    CaptchaDetectedException,
    LoginFailedException,
    TwoFactorRequiredException,
    UnusualActivityException,
)
from src.utils.helpers import random_delay, random_mouse_move
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """
    Page object for LinkedIn login page.

    Handles all login-related operations including credential entry,
    security challenge detection, and login verification.
    """

    def __init__(self, page: Page):
        """
        Initialize LoginPage.

        Args:
            page: Playwright page instance.
        """
        settings = get_settings()
        selectors = settings.get_selectors("login_page")
        super().__init__(page, selectors)

    def get_url(self) -> str:
        """
        Get the login page URL.

        Returns:
            LinkedIn login URL.
        """
        return LINKEDIN_LOGIN_URL

    async def verify_loaded(self) -> bool:
        """
        Verify that the login page is loaded.

        Returns:
            True if login page is loaded, False otherwise.
        """
        try:
            email_input_selector = self.get_selector("email_input")
            password_input_selector = self.get_selector("password_input")

            email_present = await self.is_element_present(email_input_selector)
            password_present = await self.is_element_present(password_input_selector)

            is_loaded = email_present and password_present
            logger.debug(f"Login page loaded: {is_loaded}")

            return is_loaded

        except Exception as e:
            logger.error(f"Error verifying login page: {e}")
            return False

    async def enter_email(self, email: str) -> None:
        """
        Enter email into the email input field.

        Args:
            email: Email address to enter.
        """
        logger.info("Entering email...")

        email_input_selector = self.get_selector("email_input")

        await self.click_element(email_input_selector, human_like=True)
        await random_delay(500, 1500)
        await self.type_text(email_input_selector, email, human_like=True)
        await random_delay(1000, 2000)

        logger.debug("Email entered")

    async def enter_password(self, password: str) -> None:
        """
        Enter password into the password input field.

        Args:
            password: Password to enter.
        """
        logger.info("Entering password...")

        password_input_selector = self.get_selector("password_input")

        await self.click_element(password_input_selector, human_like=True)
        await random_delay(500, 1500)
        await self.type_text(password_input_selector, password, human_like=True)
        await random_delay(1000, 3000)

        logger.debug("Password entered")

    async def click_sign_in(self) -> None:
        """Click the sign-in button."""
        logger.info("Clicking sign-in button...")

        sign_in_button_selector = self.get_selector("sign_in_button")

        await random_mouse_move(self.page)
        await self.click_element(sign_in_button_selector, human_like=True)

        logger.debug("Sign-in button clicked")

    async def is_captcha_present(self) -> bool:
        """
        Check if a CAPTCHA challenge is present.

        Returns:
            True if CAPTCHA detected, False otherwise.
        """
        for selector in CAPTCHA_SELECTORS:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    # Verify it's actually visible
                    elements = await self.page.locator(selector).all()
                    for element in elements:
                        if await element.is_visible():
                            logger.warning(f"Visible CAPTCHA detected: {selector}")
                            return True
            except Exception as e:
                logger.debug(f"Error checking CAPTCHA selector {selector}: {e}")

        return False

    async def is_2fa_present(self) -> bool:
        """
        Check if 2FA/verification challenge is present.

        Returns:
            True if 2FA detected, False otherwise.
        """
        for selector in VERIFICATION_SELECTORS:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    # Try to check visibility
                    element = self.page.locator(selector).first
                    try:
                        if await element.is_visible():
                            logger.warning(f"2FA/Verification detected: {selector}")
                            return True
                    except Exception:
                        # Text selectors might not support is_visible
                        logger.warning(f"2FA/Verification detected: {selector}")
                        return True
            except Exception as e:
                logger.debug(f"Error checking 2FA selector {selector}: {e}")

        return False

    async def detect_unusual_activity(self) -> bool:
        """
        Check for unusual activity warnings.

        Returns:
            True if unusual activity warning detected, False otherwise.
        """
        for selector in WARNING_SELECTORS:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    logger.warning(f"Unusual activity warning detected: {selector}")
                    return True
            except Exception as e:
                logger.debug(f"Error checking warning selector {selector}: {e}")

        return False

    async def detect_security_challenge(self) -> Tuple[bool, str]:
        """
        Detect any security challenges on the page.

        Returns:
            Tuple of (detected: bool, challenge_type: str).
        """
        # Check for CAPTCHA
        if await self.is_captcha_present():
            await self.take_screenshot("security_captcha_detected")
            return True, CHALLENGE_TYPE_CAPTCHA

        # Check for 2FA
        if await self.is_2fa_present():
            await self.take_screenshot("security_2fa_detected")
            return True, CHALLENGE_TYPE_2FA

        # Check for unusual activity
        if await self.detect_unusual_activity():
            await self.take_screenshot("security_unusual_activity")
            return True, CHALLENGE_TYPE_UNUSUAL_ACTIVITY

        return False, ""

    async def is_login_successful(self) -> bool:
        """
        Verify if login was successful.

        Checks if the page URL contains patterns that indicate successful login
        (feed, mynetwork, etc.).

        Returns:
            True if login successful, False otherwise.
        """
        await self.page.wait_for_load_state("domcontentloaded")

        current_url = await self.get_current_url()

        # Check for successful login URL patterns
        success_patterns = [URL_PATTERN_FEED, URL_PATTERN_MY_NETWORK]

        for pattern in success_patterns:
            if pattern in current_url:
                logger.info(f"Login successful - redirected to {pattern}")
                return True

        logger.warning(f"Login verification unclear - current URL: {current_url}")
        return False

    async def wait_for_redirect(self, timeout: int = 30000) -> bool:
        """
        Wait for redirect after login attempt.

        Args:
            timeout: Maximum wait time in milliseconds.

        Returns:
            True if redirected successfully, False otherwise.
        """
        try:
            # Wait for either feed or mynetwork URL
            await self.page.wait_for_url(
                f"**/*{URL_PATTERN_FEED}*",
                timeout=timeout,
            )
            return True
        except Exception:
            try:
                await self.page.wait_for_url(
                    f"**/*{URL_PATTERN_MY_NETWORK}*",
                    timeout=timeout,
                )
                return True
            except Exception:
                return False

    async def login(
        self,
        email: str,
        password: str,
        handle_challenges: bool = True,
        wait_time_on_challenge: int = 60,
    ) -> bool:
        """
        Perform complete login flow.

        Args:
            email: LinkedIn email.
            password: LinkedIn password.
            handle_challenges: Whether to detect and report challenges.
            wait_time_on_challenge: Time to wait if challenge detected (for manual solving).

        Returns:
            True if login successful, False otherwise.

        Raises:
            CaptchaDetectedException: If CAPTCHA is detected.
            TwoFactorRequiredException: If 2FA is required.
            UnusualActivityException: If unusual activity is detected.
            LoginFailedException: If login fails for other reasons.
        """
        logger.info("Starting LinkedIn login process...")

        try:
            # Navigate to login page
            await self.navigate()
            await self.take_screenshot("01_login_page")

            # Check for pre-login challenges
            if handle_challenges:
                detected, challenge_type = await self.detect_security_challenge()
                if detected:
                    await self._handle_challenge(challenge_type, wait_time_on_challenge)
                    return False

            # Perform random mouse movement
            await random_mouse_move(self.page)

            # Enter credentials
            await self.enter_email(email)
            await random_mouse_move(self.page)
            await self.enter_password(password)

            # Take screenshot before submitting
            await self.take_screenshot("02_credentials_entered")

            # Click sign in
            await self.click_sign_in()

            # Wait for potential redirect
            await random_delay(3000, 5000)

            # Check for post-login challenges
            if handle_challenges:
                detected, challenge_type = await self.detect_security_challenge()
                if detected:
                    await self._handle_challenge(challenge_type, wait_time_on_challenge)
                    return False

            # Verify login success
            if await self.is_login_successful():
                logger.info("Login successful!")
                await self.take_screenshot("03_login_success")
                return True
            else:
                logger.error("Login failed - unable to verify success")
                await self.take_screenshot("03_login_failed")
                raise LoginFailedException(
                    message="Login verification failed",
                    current_url=await self.get_current_url(),
                )

        except (
            CaptchaDetectedException,
            TwoFactorRequiredException,
            UnusualActivityException,
        ):
            # Re-raise known challenge exceptions
            raise

        except Exception as e:
            logger.error(f"Login error: {e}")
            await self.take_screenshot("error_login")
            raise LoginFailedException(
                message=f"Login failed: {e}",
                error_type=type(e).__name__,
            ) from e

    async def _handle_challenge(
        self,
        challenge_type: str,
        wait_time: int,
    ) -> None:
        """
        Handle detected security challenge.

        Args:
            challenge_type: Type of challenge detected.
            wait_time: Time to wait for manual intervention.

        Raises:
            Appropriate exception based on challenge type.
        """
        logger.error(f"Security challenge detected: {challenge_type}")

        # Check if we should wait for manual intervention
        settings = get_settings()
        if not settings.headless and wait_time > 0:
            logger.info(
                f"Please complete the {challenge_type} challenge manually. "
                f"Waiting {wait_time} seconds..."
            )
            await random_delay(wait_time * 1000, wait_time * 1000)

        # Raise appropriate exception
        match challenge_type:
            case _ if CHALLENGE_TYPE_CAPTCHA in challenge_type:
                raise CaptchaDetectedException(
                    captcha_type="linkedin_captcha",
                    current_url=await self.get_current_url(),
                )
            case _ if CHALLENGE_TYPE_2FA in challenge_type:
                raise TwoFactorRequiredException(
                    verification_type="unknown",
                    current_url=await self.get_current_url(),
                )
            case _ if CHALLENGE_TYPE_UNUSUAL_ACTIVITY in challenge_type:
                raise UnusualActivityException(
                    current_url=await self.get_current_url(),
                )
            case _:
                raise LoginFailedException(
                    message=f"Unknown security challenge: {challenge_type}",
                    challenge_type=challenge_type,
                )
