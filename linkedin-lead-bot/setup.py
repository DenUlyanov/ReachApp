"""Setup configuration for LinkedIn Lead Bot package."""

from pathlib import Path

from setuptools import find_packages, setup

# Read long description from README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="linkedin-lead-bot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Professional test automation framework for LinkedIn with Page Object Model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/linkedin-lead-bot",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/linkedin-lead-bot/issues",
        "Documentation": "https://github.com/yourusername/linkedin-lead-bot#readme",
        "Source Code": "https://github.com/yourusername/linkedin-lead-bot",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Pytest",
        "Typing :: Typed",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.24.0",
            "pytest-playwright>=0.4.0",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
            "ruff>=0.1.0",
            "mypy>=1.8.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "linkedin-bot=scripts.run_bot:main",
            "linkedin-bot-check=scripts.check_setup:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.txt"],
    },
    zip_safe=False,
    keywords=[
        "linkedin",
        "automation",
        "playwright",
        "page-object-model",
        "testing",
        "selenium",
        "web-scraping",
        "bot",
        "lead-generation",
    ],
)
