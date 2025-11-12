# LinkedIn Lead Bot

**Professional Test Automation Framework with Page Object Model**

A robust, maintainable, and extensible LinkedIn automation framework built with Python 3.11+, Playwright, and modern software engineering practices.

## Features

- **Page Object Model (POM)** - Clean separation of page logic and test code
- **Async/Await** - Modern Python async patterns for efficient execution
- **Anti-Detection** - Comprehensive stealth features to avoid bot detection
- **Type Safety** - Full type hints with Pydantic validation
- **Configurable** - YAML-based configuration for easy customization
- **Tested** - Unit, integration, and E2E tests with pytest
- **Documented** - Comprehensive inline documentation with Google-style docstrings
- **Modular** - SOLID principles and clean architecture

## Project Structure

```
linkedin-lead-bot/
├── src/                      # Source code
│   ├── config/              # Configuration management
│   ├── core/                # Browser and base page
│   ├── pages/               # Page objects
│   ├── utils/               # Utility modules
│   ├── bot/                 # Main bot orchestrator
│   └── exceptions.py        # Custom exceptions
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── config/                   # Configuration files
│   ├── selectors.yaml       # UI selectors
│   └── settings.yaml        # Bot settings
├── data/                     # Runtime data
│   ├── logs/                # Log files
│   └── screenshots/         # Screenshots
├── scripts/                  # Entry point scripts
│   ├── run_bot.py           # Main bot runner
│   └── check_setup.py       # Setup verification
├── .env.example             # Environment template
├── requirements.txt         # Dependencies
├── setup.py                 # Package setup
└── pytest.ini               # Test configuration
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd linkedin-lead-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your LinkedIn credentials
   ```

5. **Verify setup:**
   ```bash
   python scripts/check_setup.py
   ```

### Usage

**Run default workflow (login + feed + sales nav):**
```bash
python scripts/run_bot.py
```

**Run in headless mode:**
```bash
python scripts/run_bot.py --headless
```

**Run health check:**
```bash
python scripts/run_bot.py --health-check
```

**Login only:**
```bash
python scripts/run_bot.py --login-only
```

**Run with custom credentials:**
```bash
python scripts/run_bot.py --email user@example.com --password secret123
```

**Enable debug mode:**
```bash
python scripts/run_bot.py --slow-mo 500 --log-level DEBUG
```

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run specific test categories:**
```bash
pytest -m unit                # Unit tests only
pytest -m integration         # Integration tests only
pytest -m e2e                 # End-to-end tests only
```

**Run with coverage:**
```bash
pytest --cov=src --cov-report=html
```

**Run specific test file:**
```bash
pytest tests/unit/test_helpers.py -v
```

## Configuration

### Environment Variables (.env)

```env
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
HEADLESS_MODE=false
SLOW_MO=0
TIMEOUT=30000
MAX_LOGIN_ATTEMPTS=3
LOG_LEVEL=INFO
```

### Settings (config/settings.yaml)

Configure delays, timeouts, browser settings, and more:

```yaml
delays:
  min_typing_delay: 0.05
  max_typing_delay: 0.15
  min_action_delay: 1.0
  max_action_delay: 3.0

browser:
  viewport_width: 1920
  viewport_height: 1080
  user_agent: "Mozilla/5.0..."
```

### Selectors (config/selectors.yaml)

All UI selectors in one place:

```yaml
login_page:
  email_input: "#username"
  password_input: "#password"
  sign_in_button: 'button[type="submit"]'
```

## Architecture

### Core Components

#### BrowserManager (Singleton)
- Manages Playwright browser instance
- Implements anti-detection features
- Provides page creation and management

#### BasePage (Abstract)
- Base class for all page objects
- Provides common page operations
- Implements human-like behavior

#### Page Objects
- **LoginPage** - LinkedIn login functionality
- **FeedPage** - LinkedIn feed interactions
- **SalesNavigatorPage** - Sales Navigator operations

#### LinkedInBot (Orchestrator)
- Coordinates all bot operations
- Manages workflow execution
- Provides context manager support

### Design Patterns

- **Singleton** - BrowserManager for single browser instance
- **Page Object Model** - Clean separation of concerns
- **Factory** - Page object creation
- **Strategy** - Configurable behavior patterns
- **Observer** - Event logging and monitoring

## Anti-Detection Features

The framework includes comprehensive anti-detection measures:

- ✅ Browser automation flags disabled
- ✅ Custom user agent injection
- ✅ Random viewport sizes
- ✅ Human-like typing patterns
- ✅ Random mouse movements
- ✅ Variable action delays
- ✅ Realistic scrolling behavior
- ✅ JavaScript navigator overrides
- ✅ Plugin and language mocking

## Development

### Adding a New Page Object

1. Create a new file in `src/pages/`
2. Inherit from `BasePage`
3. Implement required methods
4. Add selectors to `config/selectors.yaml`

Example:
```python
from src.core.base_page import BasePage

class MyPage(BasePage):
    def __init__(self, page: Page):
        settings = get_settings()
        selectors = settings.get_selectors("my_page")
        super().__init__(page, selectors)

    def get_url(self) -> str:
        return "https://linkedin.com/my-page"

    async def verify_loaded(self) -> bool:
        return await self.is_element_visible(
            self.get_selector("main_element")
        )
```

### Writing Tests

```python
@pytest.mark.unit
async def test_my_function(mock_page):
    """Test description."""
    result = await my_function(mock_page)
    assert result is True
```

## Troubleshooting

### Common Issues

**1. Import errors:**
```bash
# Ensure you're in the project root
cd linkedin-lead-bot
python scripts/run_bot.py
```

**2. Browser not found:**
```bash
playwright install chromium
```

**3. Login fails:**
- Check credentials in `.env`
- Try running in non-headless mode
- Check for CAPTCHA or 2FA requirements

**4. Selectors not found:**
- LinkedIn may have changed their UI
- Update selectors in `config/selectors.yaml`

## Best Practices

1. **Never commit credentials** - Use `.env` file (gitignored)
2. **Run tests before committing** - Ensure nothing breaks
3. **Update selectors regularly** - LinkedIn changes their UI
4. **Use type hints** - Maintain type safety
5. **Write tests** - Maintain code quality
6. **Document changes** - Update docs when adding features

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and testing purposes only. Use responsibly and in accordance with LinkedIn's Terms of Service. The authors are not responsible for any misuse of this software.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the documentation
- Review the migration guide

## Acknowledgments

- Built with [Playwright](https://playwright.dev/)
- Inspired by modern test automation practices
- Following Page Object Model design pattern
