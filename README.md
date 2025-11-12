# LinkedIn Login Bot POC

A proof-of-concept automation bot for LinkedIn login with advanced anti-detection capabilities using Playwright and stealth techniques.

## Overview

This project demonstrates automated LinkedIn login with human-like behavior patterns to minimize detection. It includes comprehensive error handling, CAPTCHA/2FA detection, and detailed logging for educational and testing purposes.

**Important:** This is a proof-of-concept for educational purposes. Always comply with LinkedIn's Terms of Service and use responsibly.

## Features

### Anti-Detection Capabilities

- **Browser Fingerprinting Protection**
  - Disabled automation flags (`navigator.webdriver`)
  - Custom user agent and realistic viewport
  - Mocked plugins and Chrome runtime
  - Proper timezone and geolocation settings

- **Human-Like Behavior**
  - Random delays between actions (1-8 seconds)
  - Human-like typing with 50-150ms keystroke delays
  - Random mouse movements with natural curves
  - Random scrolling behavior
  - Realistic interaction patterns

- **Security Challenge Detection**
  - CAPTCHA detection (reCAPTCHA, image challenges)
  - 2FA/verification prompt detection
  - Unusual activity warning detection
  - Screenshot capture for all scenarios

- **Comprehensive Logging**
  - Colored console output with timestamps
  - File-based logging with rotation
  - Debug mode for detailed troubleshooting
  - Screenshot capture at key steps

## Project Structure

```
ReachApp/
├── linkedin_login_bot.py    # Main bot implementation
├── check_setup.py            # Setup verification script
├── requirements.txt          # Python dependencies
├── .env.example             # Configuration template
├── .env                     # Your credentials (DO NOT COMMIT)
├── .gitignore              # Git ignore rules
├── screenshots/            # Auto-generated screenshots
├── logs/                   # Bot execution logs
└── docs/                   # Additional documentation
    ├── README.md           # This file
    ├── QUICK_START.md      # 5-minute setup guide
    ├── START_HERE.md       # Project overview
    ├── PROJECT_STRUCTURE.md # Architecture details
    ├── TESTING_CHECKLIST.md # Testing guide
    └── ARCHITECTURE_DIAGRAM.txt # System diagrams
```

## Quick Start

See [QUICK_START.md](QUICK_START.md) for a 5-minute setup guide.

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- LinkedIn account credentials
- Internet connection

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ReachApp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

4. **Configure credentials**
   ```bash
   cp .env .env
   # Edit .env and add your LinkedIn credentials
   ```

5. **Verify setup**
   ```bash
   python check_setup.py
   ```

6. **Run the bot**
   ```bash
   python linkedin_login_bot.py
   ```

## Configuration

### Environment Variables (.env)

```env
# LinkedIn Credentials
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-secure-password

# Optional Settings
SALES_NAVIGATOR_URL=https://www.linkedin.com/sales
HEADLESS_MODE=false
TIMEOUT=30000
MAX_LOGIN_ATTEMPTS=3
LOG_LEVEL=INFO
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `LINKEDIN_EMAIL` | Your LinkedIn email | Required |
| `LINKEDIN_PASSWORD` | Your LinkedIn password | Required |
| `SALES_NAVIGATOR_URL` | Sales Navigator URL | https://www.linkedin.com/sales |
| `HEADLESS_MODE` | Run browser in background | false |
| `TIMEOUT` | Page load timeout (ms) | 30000 |
| `MAX_LOGIN_ATTEMPTS` | Login retry attempts | 3 |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING) | INFO |

## Usage

### Basic Usage

```bash
# Run with visible browser (default)
python linkedin_login_bot.py

# Run in headless mode
# Set HEADLESS_MODE=true in .env
python linkedin_login_bot.py
```

### Advanced Usage

```python
import asyncio
from src.poc.linkedin_login_bot import LinkedInBot


async def main():
    bot = LinkedInBot()
    await bot.setup_browser()

    success = await bot.login()
    if success:
        # Perform custom actions here
        await bot.navigate_to_sales_navigator()

    await bot.cleanup()


asyncio.run(main())
```

## Anti-Detection Features Explained

### 1. Browser Fingerprinting

The bot modifies browser fingerprints to appear as a regular user:

```javascript
// Removes webdriver flag
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// Mocks Chrome runtime
window.chrome = { runtime: {} };
```

### 2. Human-Like Timing

Random delays simulate human behavior:

```python
# Random delay between 1-8 seconds
await human_delay(1000, 8000)

# Typing with 50-150ms per character
await human_type(element, "text")
```

### 3. Mouse and Scroll Behavior

Natural movements prevent detection:

```python
# Random mouse movements with curves
await random_mouse_movement()

# Random scroll amounts
await random_scroll()
```

### 4. Security Challenge Detection

Monitors for common security challenges:

- CAPTCHA (reCAPTCHA, image challenges)
- Two-factor authentication prompts
- Email/phone verification
- Unusual activity warnings

## Troubleshooting

### Common Issues

#### 1. Login Fails Immediately

**Symptoms:** Bot logs in but immediately fails
**Solutions:**
- Check credentials in `.env`
- Ensure no typos in email/password
- Try logging in manually first
- Check for account restrictions

#### 2. CAPTCHA Detected

**Symptoms:** Bot detects CAPTCHA challenge
**Solutions:**
- Run in non-headless mode (`HEADLESS_MODE=false`)
- Complete CAPTCHA manually
- Wait 24 hours before retrying
- Use different IP/network
- Avoid running bot too frequently

#### 3. 2FA/Verification Required

**Symptoms:** LinkedIn asks for verification code
**Solutions:**
- Complete verification manually (non-headless mode)
- Add trusted device to LinkedIn account
- Use app-based 2FA for faster completion
- Consider disabling 2FA for testing (not recommended)

#### 4. Playwright Not Installed

**Symptoms:** `playwright command not found`
**Solutions:**
```bash
pip install playwright
playwright install chromium
```

#### 5. Module Import Errors

**Symptoms:** `ModuleNotFoundError`
**Solutions:**
```bash
pip install -r requirements.txt
python check_setup.py
```

#### 6. Screenshots Directory Error

**Symptoms:** Cannot create screenshots
**Solutions:**
```bash
mkdir screenshots
mkdir logs
chmod 755 screenshots logs
```

### Debug Mode

Enable detailed logging:

```env
LOG_LEVEL=DEBUG
```

This will show:
- All browser actions
- Mouse movements
- Timing delays
- Element interactions

### Checking Logs

Logs are saved in `logs/` directory:

```bash
# View latest log
ls -lt logs/ | head -n 1

# Tail live log
tail -f logs/linkedin_bot_*.log
```

## Security Best Practices

### Credential Safety

1. **Never commit `.env` file**
   - Already in `.gitignore`
   - Use `.env.example` as template

2. **Use strong passwords**
   - Unique password for testing account
   - Consider dedicated test account

3. **Secure credential storage**
   ```bash
   chmod 600 .env  # Only owner can read/write
   ```

### Account Safety

1. **Rate Limiting**
   - Don't run bot more than 3-5 times per day
   - Add delays between sessions
   - Monitor for warning signs

2. **Detection Indicators**
   - CAPTCHA challenges
   - Email verification requests
   - Account warnings
   - Unusual activity notifications

3. **Risk Mitigation**
   - Use test account first
   - Start with headless=false
   - Monitor LinkedIn emails
   - Keep screenshots for debugging

### Legal Compliance

1. **Terms of Service**
   - Review LinkedIn's ToS
   - Understand automation restrictions
   - Use responsibly and ethically

2. **Data Privacy**
   - Only access your own account
   - Don't scrape user data
   - Respect privacy regulations

3. **Educational Use**
   - This is a POC for learning
   - Not for production use
   - Understand the technology

## Testing

### Manual Testing

1. **Run setup check**
   ```bash
   python check_setup.py
   ```

2. **Test with visible browser**
   ```bash
   # Set HEADLESS_MODE=false
   python linkedin_login_bot.py
   ```

3. **Review screenshots**
   ```bash
   ls -lt screenshots/
   ```

4. **Check logs**
   ```bash
   cat logs/linkedin_bot_*.log
   ```

### Automated Testing

```bash
# Run pytest tests (when implemented)
pytest tests/ -v
```

See [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) for comprehensive testing guide.

## Development Roadmap

See [START_HERE.md](START_HERE.md) for full development roadmap with 9 phases:

1. ✅ Basic Setup
2. ✅ Simple Login
3. ✅ Anti-Detection
4. 🔄 Error Handling
5. ⏳ Sales Navigator
6. ⏳ Profile Viewing
7. ⏳ Connection Requests
8. ⏳ Messaging
9. ⏳ Data Export

## Contributing

This is a proof-of-concept project. If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for educational purposes only. The authors are not responsible for any misuse or violations of LinkedIn's Terms of Service. Use at your own risk and always comply with applicable laws and terms of service.

## Support

- Check [QUICK_START.md](QUICK_START.md) for setup issues
- Review [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) for debugging
- See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture details
- Read [START_HERE.md](START_HERE.md) for learning roadmap

## Acknowledgments

- Built with [Playwright](https://playwright.dev/)
- Uses [playwright-stealth](https://github.com/AtuboDad/playwright_stealth) concepts
- Inspired by automation best practices

## Version

Current Version: 1.0.0 (POC)
Last Updated: 2025-11-08
