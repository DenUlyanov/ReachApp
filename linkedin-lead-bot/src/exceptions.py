"""
Custom exceptions for the LinkedIn Bot framework.

This module defines a hierarchy of custom exceptions used throughout
the bot for better error handling and debugging.
"""


class LinkedInBotException(Exception):
    """Base exception for all LinkedIn Bot errors."""

    def __init__(self, message: str, details: dict[str, any] | None = None):
        """
        Initialize LinkedInBotException.

        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional context.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation with details if available."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class LoginFailedException(LinkedInBotException):
    """Raised when LinkedIn login fails."""

    def __init__(self, message: str = "Login failed", **kwargs):
        """
        Initialize LoginFailedException.

        Args:
            message: Error message describing the login failure.
            **kwargs: Additional details about the failure.
        """
        super().__init__(message, details=kwargs)


class CaptchaDetectedException(LinkedInBotException):
    """Raised when a CAPTCHA challenge is detected."""

    def __init__(
        self,
        message: str = "CAPTCHA challenge detected",
        captcha_type: str | None = None,
        **kwargs,
    ):
        """
        Initialize CaptchaDetectedException.

        Args:
            message: Error message.
            captcha_type: Type of CAPTCHA (e.g., 'recaptcha', 'hcaptcha').
            **kwargs: Additional details.
        """
        details = kwargs
        if captcha_type:
            details["captcha_type"] = captcha_type
        super().__init__(message, details=details)


class TwoFactorRequiredException(LinkedInBotException):
    """Raised when 2FA verification is required."""

    def __init__(
        self,
        message: str = "Two-factor authentication required",
        verification_type: str | None = None,
        **kwargs,
    ):
        """
        Initialize TwoFactorRequiredException.

        Args:
            message: Error message.
            verification_type: Type of verification (e.g., 'email', 'phone', 'app').
            **kwargs: Additional details.
        """
        details = kwargs
        if verification_type:
            details["verification_type"] = verification_type
        super().__init__(message, details=details)


class UnusualActivityException(LinkedInBotException):
    """Raised when LinkedIn detects unusual activity."""

    def __init__(
        self,
        message: str = "Unusual activity detected on account",
        **kwargs,
    ):
        """
        Initialize UnusualActivityException.

        Args:
            message: Error message.
            **kwargs: Additional details.
        """
        super().__init__(message, details=kwargs)


class NavigationException(LinkedInBotException):
    """Raised when page navigation fails."""

    def __init__(
        self,
        message: str = "Navigation failed",
        url: str | None = None,
        **kwargs,
    ):
        """
        Initialize NavigationException.

        Args:
            message: Error message.
            url: The URL that failed to load.
            **kwargs: Additional details.
        """
        details = kwargs
        if url:
            details["url"] = url
        super().__init__(message, details=details)


class ElementNotFoundException(LinkedInBotException):
    """Raised when a required page element is not found."""

    def __init__(
        self,
        message: str = "Required element not found",
        selector: str | None = None,
        **kwargs,
    ):
        """
        Initialize ElementNotFoundException.

        Args:
            message: Error message.
            selector: The selector that failed to find the element.
            **kwargs: Additional details.
        """
        details = kwargs
        if selector:
            details["selector"] = selector
        super().__init__(message, details=details)


class BrowserInitializationException(LinkedInBotException):
    """Raised when browser initialization fails."""

    def __init__(
        self,
        message: str = "Failed to initialize browser",
        **kwargs,
    ):
        """
        Initialize BrowserInitializationException.

        Args:
            message: Error message.
            **kwargs: Additional details.
        """
        super().__init__(message, details=kwargs)


class ConfigurationException(LinkedInBotException):
    """Raised when configuration is invalid or missing."""

    def __init__(
        self,
        message: str = "Configuration error",
        config_key: str | None = None,
        **kwargs,
    ):
        """
        Initialize ConfigurationException.

        Args:
            message: Error message.
            config_key: The configuration key that caused the error.
            **kwargs: Additional details.
        """
        details = kwargs
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details=details)


class TimeoutException(LinkedInBotException):
    """Raised when an operation times out."""

    def __init__(
        self,
        message: str = "Operation timed out",
        timeout: float | None = None,
        operation: str | None = None,
        **kwargs,
    ):
        """
        Initialize TimeoutException.

        Args:
            message: Error message.
            timeout: The timeout value in seconds.
            operation: Description of the operation that timed out.
            **kwargs: Additional details.
        """
        details = kwargs
        if timeout is not None:
            details["timeout"] = timeout
        if operation:
            details["operation"] = operation
        super().__init__(message, details=details)
