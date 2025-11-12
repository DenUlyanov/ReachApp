#!/usr/bin/env python3
"""
Main entry point for running the LinkedIn Bot.

This script provides a command-line interface for executing the bot
with various options and workflows.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bot.linkedin_bot import LinkedInBot
from src.config.settings import get_settings
from src.exceptions import (
    CaptchaDetectedException,
    ConfigurationException,
    LinkedInBotException,
    LoginFailedException,
    TwoFactorRequiredException,
    UnusualActivityException,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="LinkedIn Lead Bot - Professional Test Automation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python run_bot.py

  # Run in headless mode
  python run_bot.py --headless

  # Run health check only
  python run_bot.py --health-check

  # Run demo workflow
  python run_bot.py --demo

  # Run with custom credentials
  python run_bot.py --email user@example.com --password secret123

  # Enable slow motion for debugging
  python run_bot.py --slow-mo 500
        """,
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )

    parser.add_argument(
        "--slow-mo",
        type=int,
        metavar="MS",
        help="Slow motion delay in milliseconds (for debugging)",
    )

    parser.add_argument(
        "--email",
        type=str,
        metavar="EMAIL",
        help="LinkedIn email (overrides .env)",
    )

    parser.add_argument(
        "--password",
        type=str,
        metavar="PASSWORD",
        help="LinkedIn password (overrides .env)",
    )

    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run health check only (no login)",
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo workflow (login -> feed -> sales nav)",
    )

    parser.add_argument(
        "--login-only",
        action="store_true",
        help="Perform login only and exit",
    )

    parser.add_argument(
        "--sales-nav",
        action="store_true",
        help="Navigate to Sales Navigator after login",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    return parser.parse_args()


async def run_health_check(bot: LinkedInBot) -> int:
    """
    Run health check workflow.

    Args:
        bot: Initialized LinkedInBot instance.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    logger.info("🔍 Running health check...")

    try:
        health = await bot.run_health_check()

        # Print results
        print("\n" + "=" * 60)
        print("  HEALTH CHECK RESULTS")
        print("=" * 60)

        for key, value in health.items():
            if isinstance(value, bool):
                status = "✅ PASS" if value else "❌ FAIL"
                print(f"{status} - {key}")
            elif key != "error" and key != "sales_nav_details":
                print(f"ℹ️  {key}: {value}")

        if "error" in health:
            print(f"\n❌ Error: {health['error']}")

        print("=" * 60 + "\n")

        # Determine overall success
        critical_checks = ["browser_initialized", "credentials_configured"]
        all_critical_passed = all(health.get(k, False) for k in critical_checks)

        if all_critical_passed:
            logger.info("✅ Health check passed!")
            return 0
        else:
            logger.error("❌ Health check failed!")
            return 1

    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return 1


async def run_login_workflow(
    bot: LinkedInBot,
    email: str | None = None,
    password: str | None = None,
) -> int:
    """
    Run login-only workflow.

    Args:
        bot: Initialized LinkedInBot instance.
        email: Optional email override.
        password: Optional password override.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    logger.info("🔐 Running login workflow...")

    try:
        success = await bot.login(email=email, password=password)

        if success:
            logger.info("✅ Login successful!")
            return 0
        else:
            logger.error("❌ Login failed!")
            return 1

    except CaptchaDetectedException as e:
        logger.error(f"❌ CAPTCHA detected: {e}")
        return 1

    except TwoFactorRequiredException as e:
        logger.error(f"❌ 2FA required: {e}")
        return 1

    except UnusualActivityException as e:
        logger.error(f"❌ Unusual activity detected: {e}")
        return 1

    except LoginFailedException as e:
        logger.error(f"❌ Login failed: {e}")
        return 1

    except Exception as e:
        logger.error(f"❌ Unexpected error during login: {e}")
        return 1


async def run_sales_nav_workflow(
    bot: LinkedInBot,
    email: str | None = None,
    password: str | None = None,
) -> int:
    """
    Run workflow to navigate to Sales Navigator.

    Args:
        bot: Initialized LinkedInBot instance.
        email: Optional email override.
        password: Optional password override.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    logger.info("🚀 Running Sales Navigator workflow...")

    try:
        # Login first
        success = await bot.login(email=email, password=password)
        if not success:
            logger.error("❌ Login failed!")
            return 1

        # Navigate to Sales Navigator
        success = await bot.navigate_to_sales_navigator()

        if success:
            logger.info("✅ Successfully navigated to Sales Navigator!")
            return 0
        else:
            logger.error("❌ Failed to navigate to Sales Navigator!")
            return 1

    except LinkedInBotException as e:
        logger.error(f"❌ Bot error: {e}")
        return 1

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1


async def main() -> int:
    """
    Main entry point for the bot.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    args = parse_arguments()

    # Set log level
    from src.utils.logger import set_all_log_levels

    set_all_log_levels(args.log_level)

    # Print banner
    print("\n" + "=" * 60)
    print("  LinkedIn Lead Bot - Professional Test Automation Framework")
    print("=" * 60 + "\n")

    try:
        # Initialize bot
        async with LinkedInBot() as bot:
            await bot.initialize(
                headless=args.headless,
                slow_mo=args.slow_mo,
            )

            # Determine workflow
            if args.health_check:
                return await run_health_check(bot)

            elif args.demo:
                logger.info("🎬 Running demo workflow...")
                await bot.run_demo_workflow()
                return 0

            elif args.login_only:
                return await run_login_workflow(bot, args.email, args.password)

            elif args.sales_nav:
                return await run_sales_nav_workflow(bot, args.email, args.password)

            else:
                # Default: run demo workflow
                logger.info("🎬 Running default demo workflow...")
                await bot.run_demo_workflow()
                return 0

    except ConfigurationException as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("Please check your .env file and configuration files.")
        return 1

    except KeyboardInterrupt:
        logger.info("\n⚠️  Bot stopped by user (Ctrl+C)")
        return 130

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
