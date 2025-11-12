"""
Global constants for the LinkedIn Bot framework.

This module contains all constant values used throughout the application,
following the principle of avoiding hardcoded strings and magic numbers.
"""

from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Root directory of the project
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Configuration directories
CONFIG_DIR = PROJECT_ROOT / "config"
SELECTORS_FILE = CONFIG_DIR / "selectors.yaml"
SETTINGS_FILE = CONFIG_DIR / "settings.yaml"

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
LOGS_DIR = DATA_DIR / "logs"

# Source directories
SRC_DIR = PROJECT_ROOT / "src"

# ============================================================================
# LINKEDIN URLs
# ============================================================================

LINKEDIN_BASE_URL = "https://www.linkedin.com"
LINKEDIN_LOGIN_URL = f"{LINKEDIN_BASE_URL}/login"
LINKEDIN_FEED_URL = f"{LINKEDIN_BASE_URL}/feed"
LINKEDIN_MY_NETWORK_URL = f"{LINKEDIN_BASE_URL}/mynetwork"
SALES_NAVIGATOR_BASE_URL = "https://www.linkedin.com/sales"
SALES_NAVIGATOR_SEARCH_URL = f"{SALES_NAVIGATOR_BASE_URL}/search/company"

# ============================================================================
# BROWSER CONFIGURATION
# ============================================================================

# Default browser arguments for anti-detection
DEFAULT_BROWSER_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-web-security",
    "--disable-features=IsolateOrigins,site-per-process",
]

# Browser arguments for non-headless mode
NON_HEADLESS_ARGS = [
    "--start-maximized",
    "--window-position=0,0",
]

# Default viewport size
DEFAULT_VIEWPORT_WIDTH = 1920
DEFAULT_VIEWPORT_HEIGHT = 1080

# Default user agent (up-to-date Chrome on Windows)
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

# Default locale and timezone
DEFAULT_LOCALE = "en-US"
DEFAULT_TIMEZONE = "America/New_York"

# Default geolocation (New York City)
DEFAULT_GEOLOCATION = {
    "latitude": 40.7128,
    "longitude": -74.0060,
}

# ============================================================================
# TIMING CONSTANTS (milliseconds unless otherwise specified)
# ============================================================================

# Default timeouts
DEFAULT_TIMEOUT = 30_000  # 30 seconds
DEFAULT_NAVIGATION_TIMEOUT = 60_000  # 60 seconds
DEFAULT_ACTION_TIMEOUT = 10_000  # 10 seconds

# Human-like delays (min, max in milliseconds)
MIN_TYPING_DELAY = 50
MAX_TYPING_DELAY = 150

MIN_ACTION_DELAY = 1_000
MAX_ACTION_DELAY = 3_000

MIN_PAGE_LOAD_DELAY = 2_000
MAX_PAGE_LOAD_DELAY = 4_000

MIN_SCROLL_DELAY = 500
MAX_SCROLL_DELAY = 2_000

# Mouse movement
MIN_MOUSE_STEPS = 5
MAX_MOUSE_STEPS = 15

# Retry configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 10

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Log levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Colored log format for console
COLORED_LOG_FORMAT = "%(log_color)s%(asctime)s - %(levelname)s - %(message)s"

# Log colors
LOG_COLORS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red,bg_white",
}

# Log file naming
LOG_FILE_PREFIX = "linkedin_bot"
LOG_FILE_SUFFIX = ".log"
LOG_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Log rotation
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# ============================================================================
# SCREENSHOT CONFIGURATION
# ============================================================================

SCREENSHOT_FORMAT = "png"
SCREENSHOT_QUALITY = 90
SCREENSHOT_FULL_PAGE = True

# ============================================================================
# SECURITY CHALLENGE DETECTION
# ============================================================================

# CAPTCHA selectors
CAPTCHA_SELECTORS = [
    'iframe[src*="recaptcha"][src*="bframe"]',
    'iframe[title*="recaptcha"]',
    '[id*="captcha"]:visible',
    '[class*="captcha"]:visible',
]

# 2FA/Verification selectors
VERIFICATION_SELECTORS = [
    'text=/enter.*verification.*code/i',
    'text=/enter.*security.*code/i',
    'text=/two.*factor/i',
    'text=/6.*digit.*code/i',
    'input[name*="verification"]',
    'input[name*="pin"]',
    'input[id*="verification"]',
    'input[id*="challenge"]',
    '[data-test-id*="verification"]',
    'input[id="input__email_verification_pin"]',
    'input[id="input__phone_verification_pin"]',
]

# Unusual activity warning selectors
WARNING_SELECTORS = [
    'text=/unusual.*activity/i',
    'text=/suspicious.*activity/i',
    'text=/temporarily.*restricted/i',
    'text=/account.*restricted/i',
]

# Security challenge types
CHALLENGE_TYPE_CAPTCHA = "CAPTCHA"
CHALLENGE_TYPE_2FA = "2FA"
CHALLENGE_TYPE_VERIFICATION = "Verification"
CHALLENGE_TYPE_UNUSUAL_ACTIVITY = "Unusual Activity"

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

ENV_LINKEDIN_EMAIL = "LINKEDIN_EMAIL"
ENV_LINKEDIN_PASSWORD = "LINKEDIN_PASSWORD"
ENV_SALES_NAVIGATOR_URL = "SALES_NAVIGATOR_URL"
ENV_HEADLESS_MODE = "HEADLESS_MODE"
ENV_TIMEOUT = "TIMEOUT"
ENV_MAX_LOGIN_ATTEMPTS = "MAX_LOGIN_ATTEMPTS"
ENV_LOG_LEVEL = "LOG_LEVEL"
ENV_SLOW_MO = "SLOW_MO"

# ============================================================================
# PAGE IDENTIFIERS
# ============================================================================

# URL patterns for page identification
URL_PATTERN_FEED = "feed"
URL_PATTERN_MY_NETWORK = "mynetwork"
URL_PATTERN_LOGIN = "login"
URL_PATTERN_SALES_NAV = "sales"

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

# Test markers
TEST_MARKER_UNIT = "unit"
TEST_MARKER_INTEGRATION = "integration"
TEST_MARKER_E2E = "e2e"
TEST_MARKER_SLOW = "slow"

# Test timeouts
TEST_UNIT_TIMEOUT = 10  # seconds
TEST_INTEGRATION_TIMEOUT = 60  # seconds
TEST_E2E_TIMEOUT = 300  # seconds (5 minutes)

# ============================================================================
# HTTP/NETWORK CONSTANTS
# ============================================================================

HTTP_TIMEOUT = 30  # seconds
HTTP_MAX_REDIRECTS = 10
HTTP_USER_AGENT = DEFAULT_USER_AGENT

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURE_SCREENSHOT_ON_ERROR = True
FEATURE_SCREENSHOT_ON_SUCCESS = True
FEATURE_VIDEO_RECORDING = False
FEATURE_TRACE_RECORDING = False
FEATURE_PERFORMANCE_MONITORING = False

# ============================================================================
# VALIDATION PATTERNS
# ============================================================================

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
URL_PATTERN = r"^https?://.*"

# ============================================================================
# STATUS MESSAGES
# ============================================================================

STATUS_INITIALIZING = "Initializing"
STATUS_READY = "Ready"
STATUS_RUNNING = "Running"
STATUS_PAUSED = "Paused"
STATUS_COMPLETED = "Completed"
STATUS_FAILED = "Failed"
STATUS_STOPPED = "Stopped"

# ============================================================================
# EMOJIS (optional, for enhanced logging)
# ============================================================================

EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_INFO = "ℹ️"
EMOJI_ROCKET = "🚀"
EMOJI_ROBOT = "🤖"
EMOJI_LOCK = "🔒"
EMOJI_KEY = "🔑"
EMOJI_MAGNIFYING_GLASS = "🔍"
EMOJI_HOURGLASS = "⏳"
EMOJI_CHECKMARK = "✓"
EMOJI_CROSS = "✗"
