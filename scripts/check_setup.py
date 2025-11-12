#!/usr/bin/env python3
"""
Setup Verification Script for LinkedIn Bot.

This script validates that all dependencies and configurations are
properly installed and configured.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(text: str) -> None:
    """Print formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_python_version() -> bool:
    """Verify Python version is 3.11+."""
    print_header("Checking Python Version")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 11:
        print("✅ Python version is compatible (3.11+)")
        return True
    else:
        print("❌ Python 3.11+ required for modern features")
        print(f"   Current version: {version.major}.{version.minor}")
        return False


def check_modules() -> bool:
    """Check if required Python modules are installed."""
    print_header("Checking Python Modules")

    required_modules = [
        ("playwright", "playwright"),
        ("pydantic", "pydantic"),
        ("pydantic_settings", "pydantic-settings"),
        ("yaml", "pyyaml"),
        ("dotenv", "python-dotenv"),
        ("colorlog", "colorlog"),
        ("pytest", "pytest"),
        ("pytest_asyncio", "pytest-asyncio"),
        ("pytest_playwright", "pytest-playwright"),
        ("pytest_mock", "pytest-mock"),
    ]

    all_installed = True

    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - NOT INSTALLED")
            all_installed = False

    if all_installed:
        print("\n✅ All required modules are installed!")
    else:
        print("\n❌ Some modules are missing. Run: pip install -r requirements.txt")

    return all_installed


def check_playwright_browsers() -> bool:
    """Check if Playwright browsers are installed."""
    print_header("Checking Playwright Browsers")

    try:
        import subprocess

        result = subprocess.run(
            ["playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ Playwright browsers check passed")
            print("   Chromium browser appears to be installed")
            return True
        else:
            print("❌ Playwright browsers may not be installed")
            print("   Run: playwright install chromium")
            return False

    except FileNotFoundError:
        print("❌ Playwright command not found")
        print("   Install Playwright: pip install playwright")
        print("   Then install browsers: playwright install chromium")
        return False
    except Exception as e:
        print(f"⚠️  Warning: Could not verify Playwright browsers: {e}")
        print("   If you just installed Playwright, run: playwright install chromium")
        return False


def check_directory_structure() -> bool:
    """Verify directory structure is correct."""
    print_header("Checking Directory Structure")

    base_dir = Path(__file__).parent.parent

    required_dirs = [
        "src/config",
        "src/core",
        "src/pages",
        "src/utils",
        "src/bot",
        "config",
        "data/screenshots",
        "data/logs",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "scripts",
    ]

    all_exist = True

    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - MISSING")
            all_exist = False

    return all_exist


def check_config_files() -> bool:
    """Check if configuration files exist."""
    print_header("Checking Configuration Files")

    base_dir = Path(__file__).parent.parent

    required_files = [
        ("config/selectors.yaml", True),
        ("config/settings.yaml", True),
        (".env", False),  # Optional, not required for tests
        (".env.example", True),
    ]

    all_exist = True

    for file_path, required in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        elif required:
            print(f"❌ {file_path} - MISSING (required)")
            all_exist = False
        else:
            print(f"⚠️  {file_path} - MISSING (optional)")

    return all_exist


def check_env_configuration() -> bool:
    """Check .env file configuration."""
    print_header("Checking Environment Configuration")

    base_dir = Path(__file__).parent.parent
    env_file = base_dir / ".env"

    if not env_file.exists():
        print("⚠️  .env file not found (optional for testing)")
        print("   Copy .env.example to .env for production use")
        return True  # Not critical for tests

    print("✅ .env file exists")

    # Check for required variables
    required_vars = ["LINKEDIN_EMAIL", "LINKEDIN_PASSWORD"]
    configured_vars = []

    try:
        with open(env_file, "r") as f:
            content = f.read()

            for var in required_vars:
                if var in content:
                    # Check if it has a non-empty value
                    for line in content.split("\n"):
                        if line.startswith(f"{var}="):
                            value = line.split("=", 1)[1].strip()
                            if value and not value.startswith("your-"):
                                print(f"✅ {var} is configured")
                                configured_vars.append(var)
                            else:
                                print(f"⚠️  {var} is not configured (using placeholder)")
                            break
                else:
                    print(f"⚠️  {var} is missing from .env")

        if len(configured_vars) == len(required_vars):
            print("\n✅ All credentials configured")
            return True
        else:
            print("\n⚠️  Some credentials not configured")
            print("   Bot will work for testing but cannot log in to LinkedIn")
            return True  # Not critical for setup check

    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False


def check_source_files() -> bool:
    """Check if main source files exist."""
    print_header("Checking Source Files")

    base_dir = Path(__file__).parent.parent

    required_files = [
        "src/__init__.py",
        "src/config/settings.py",
        "src/config/constants.py",
        "src/core/browser_manager.py",
        "src/core/base_page.py",
        "src/pages/login_page.py",
        "src/pages/feed_page.py",
        "src/pages/sales_navigator_page.py",
        "src/bot/linkedin_bot.py",
        "src/utils/logger.py",
        "src/utils/helpers.py",
        "src/utils/screenshot_manager.py",
        "src/exceptions.py",
    ]

    all_exist = True

    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False

    return all_exist


def check_imports() -> bool:
    """Test if main modules can be imported."""
    print_header("Checking Module Imports")

    modules_to_import = [
        ("src.config", "Configuration module"),
        ("src.core", "Core modules"),
        ("src.pages", "Page objects"),
        ("src.bot", "Bot orchestrator"),
        ("src.utils", "Utility modules"),
        ("src.exceptions", "Custom exceptions"),
    ]

    all_imported = True

    for module_name, description in modules_to_import:
        try:
            __import__(module_name)
            print(f"✅ {description} ({module_name})")
        except ImportError as e:
            print(f"❌ {description} ({module_name}) - IMPORT ERROR")
            print(f"   Error: {e}")
            all_imported = False
        except Exception as e:
            print(f"⚠️  {description} ({module_name}) - WARNING")
            print(f"   Error: {e}")

    return all_imported


def run_all_checks() -> bool:
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("  LINKEDIN BOT - SETUP VERIFICATION")
    print("  Professional Test Automation Framework")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version),
        ("Python Modules", check_modules),
        ("Playwright Browsers", check_playwright_browsers),
        ("Directory Structure", check_directory_structure),
        ("Configuration Files", check_config_files),
        ("Environment Config", check_env_configuration),
        ("Source Files", check_source_files),
        ("Module Imports", check_imports),
    ]

    results = {}

    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ Error during {check_name} check: {e}")
            results[check_name] = False

    # Print summary
    print_header("SUMMARY")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")

    print(f"\n📊 Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All checks passed! You're ready to run the bot.")
        print("\nNext steps:")
        print("  1. Configure .env with your LinkedIn credentials (if needed)")
        print("  2. Run: python scripts/run_bot.py --help")
        print("  3. Try: python scripts/run_bot.py --health-check")
        print("  4. Run tests: pytest tests/")
        return True
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Install browsers: playwright install chromium")
        print("  - Create .env: cp .env.example .env")
        return False


def main() -> int:
    """Entry point."""
    try:
        success = run_all_checks()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Check interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
