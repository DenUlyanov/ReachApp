#!/usr/bin/env python3
"""
Setup Verification Script
Validates that all dependencies and configurations are properly installed
"""

import sys
import os
from pathlib import Path
import subprocess


def print_header(text):
    """Print formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_python_version():
    """Verify Python version is 3.8+"""
    print_header("Checking Python Version")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 8:
        print("✓ Python version is compatible (3.8+)")
        return True
    else:
        print("✗ Python 3.8+ required")
        return False


def check_modules():
    """Check if required Python modules are installed"""
    print_header("Checking Python Modules")

    required_modules = [
        'playwright',
        'dotenv',
        'colorlog',
        'pytest',
        'pytest_asyncio',
    ]

    all_installed = True

    for module in required_modules:
        try:
            if module == 'dotenv':
                __import__('dotenv')
            elif module == 'pytest_asyncio':
                __import__('pytest_asyncio')
            else:
                __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - NOT INSTALLED")
            all_installed = False

    if all_installed:
        print("\nAll required modules are installed!")
    else:
        print("\nSome modules are missing. Run: pip install -r requirements.txt")

    return all_installed


def check_playwright_browsers():
    """Check if Playwright browsers are installed"""
    print_header("Checking Playwright Browsers")

    try:
        result = subprocess.run(
            ['playwright', 'install', '--dry-run', 'chromium'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("✓ Playwright browsers check passed")
            print("Chromium browser appears to be installed")
            return True
        else:
            print("✗ Playwright browsers may not be installed")
            print("Run: playwright install chromium")
            return False

    except FileNotFoundError:
        print("✗ Playwright command not found")
        print("Install Playwright: pip install playwright")
        print("Then install browsers: playwright install chromium")
        return False
    except Exception as e:
        print(f"Warning: Could not verify Playwright browsers: {e}")
        print("If you just installed Playwright, run: playwright install chromium")
        return False


def check_env_file():
    """Check if .env file exists and has required variables"""
    print_header("Checking Environment Configuration")

    env_file = Path('.env')
    env_example = Path('.env')

    if not env_file.exists():
        print("✗ .env file not found")
        if env_example.exists():
            print(f"Copy {env_example} to .env and fill in your credentials")
            print(f"Command: cp {env_example} .env")
        return False

    print("✓ .env file exists")

    # Check for required variables
    required_vars = ['LINKEDIN_EMAIL', 'LINKEDIN_PASSWORD']
    missing_vars = []

    try:
        with open(env_file, 'r') as f:
            content = f.read()

            for var in required_vars:
                if var not in content:
                    missing_vars.append(var)
                elif f"{var}=your-" in content or f"{var}=" in content and content.split(f"{var}=")[1].split('\n')[0].strip() == "":
                    print(f"⚠ {var} is not configured (using placeholder)")
                else:
                    print(f"✓ {var} is configured")

        if missing_vars:
            print(f"\n✗ Missing variables: {', '.join(missing_vars)}")
            return False

        return True

    except Exception as e:
        print(f"✗ Error reading .env file: {e}")
        return False


def check_directories():
    """Check if required directories exist or can be created"""
    print_header("Checking Directories")

    directories = ['screenshots', 'logs']
    all_ok = True

    for dir_name in directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✓ {dir_name}/ exists")
        else:
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"✓ {dir_name}/ created")
            except Exception as e:
                print(f"✗ Cannot create {dir_name}/: {e}")
                all_ok = False

    return all_ok


def check_file_structure():
    """Verify all required project files exist"""
    print_header("Checking Project Files")

    required_files = [
        'src/poc/linkedin_login_bot.py',
        'requirements.txt',
        '.env',
        '.gitignore',
        'README.md',
    ]

    all_exist = True

    for filename in required_files:
        file_path = Path(filename)
        if file_path.exists():
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} - MISSING")
            all_exist = False

    return all_exist


def run_all_checks():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("  LINKEDIN LOGIN BOT - SETUP VERIFICATION")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version),
        ("Python Modules", check_modules),
        ("Playwright Browsers", check_playwright_browsers),
        ("Environment Config", check_env_file),
        ("Project Directories", check_directories),
        ("Project Files", check_file_structure),
    ]

    results = {}

    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n✗ Error during {check_name} check: {e}")
            results[check_name] = False

    # Print summary
    print_header("SUMMARY")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {check_name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All checks passed! You're ready to run the bot.")
        print("\nNext steps:")
        print("1. Ensure .env has your LinkedIn credentials")
        print("2. Run: python linkedin_login_bot.py")
        return True
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Install browsers: playwright install chromium")
        print("- Create .env: cp .env .env")
        print("- Configure credentials in .env")
        return False


def main():
    """Entry point"""
    try:
        success = run_all_checks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCheck interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
