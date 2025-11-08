# Quick Start Guide

Get the LinkedIn Login Bot running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] pip installed (`pip --version`)
- [ ] Internet connection
- [ ] LinkedIn account credentials

## 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

**Expected output:**
```
Successfully installed playwright-1.48.0 ...
Downloading Chromium...
```

### Step 2: Configure Credentials (1 minute)

```bash
# Copy the example config
cp .env.example .env

# Edit .env with your favorite editor
nano .env
# OR
vim .env
# OR
code .env
```

**Update these lines:**
```env
LINKEDIN_EMAIL=your-actual-email@example.com
LINKEDIN_PASSWORD=your-actual-password
```

**Save and close the file.**

### Step 3: Verify Setup (1 minute)

```bash
python check_setup.py
```

**Expected output:**
```
============================================================
  LINKEDIN LOGIN BOT - SETUP VERIFICATION
============================================================
✓ PASS - Python Version
✓ PASS - Python Modules
✓ PASS - Playwright Browsers
✓ PASS - Environment Config
✓ PASS - Project Directories
✓ PASS - Project Files

Passed: 6/6

🎉 All checks passed! You're ready to run the bot.
```

### Step 4: Run the Bot (1 minute)

```bash
python linkedin_login_bot.py
```

**What you'll see:**
1. Browser window opens (Chrome)
2. Navigates to LinkedIn login page
3. Types your email (with human-like delays)
4. Types your password (with human-like delays)
5. Clicks login button
6. Logs success or any issues

**Screenshots saved to:** `screenshots/`
**Logs saved to:** `logs/`

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "playwright command not found"

**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Issue: "CAPTCHA detected"

**What this means:** LinkedIn is asking you to verify you're human

**Solution:**
1. The browser stays open (in non-headless mode)
2. Complete the CAPTCHA manually
3. Wait for the bot to continue

**Prevention:**
- Don't run the bot too frequently (max 3-5 times/day)
- Use different networks/IPs
- Wait 24 hours between heavy usage

### Issue: "2FA/Verification required"

**What this means:** LinkedIn wants to verify your device

**Solution:**
1. Complete the verification manually in the browser window
2. Use your phone/email to get the code
3. Enter the code in the browser
4. The bot will continue after verification

**Prevention:**
- Add this device as "trusted" in LinkedIn settings
- Keep the same device/browser for testing

### Issue: Login fails silently

**Check these:**
```bash
# 1. Verify credentials in .env
cat .env

# 2. Check the latest log
ls -lt logs/ | head -n 2
cat logs/linkedin_bot_*.log

# 3. Check screenshots
ls -lt screenshots/ | head -n 5
```

**Common causes:**
- Wrong credentials in `.env`
- Account locked/restricted
- LinkedIn changed their page layout

## Configuration Options

### Run in Headless Mode (invisible browser)

Edit `.env`:
```env
HEADLESS_MODE=true
```

**When to use:**
- Production environments
- Server deployments
- Automated testing

**When NOT to use:**
- First-time testing
- Debugging issues
- Need to see what's happening
- CAPTCHA/2FA challenges

### Enable Debug Logging

Edit `.env`:
```env
LOG_LEVEL=DEBUG
```

**What you'll see:**
- Every mouse movement
- Every keystroke delay
- Element searches
- Page navigation details

**Use for:**
- Troubleshooting failures
- Understanding bot behavior
- Development

### Adjust Timeouts

Edit `.env`:
```env
TIMEOUT=60000  # 60 seconds (default: 30000)
```

**When to increase:**
- Slow internet connection
- Bot timing out during page loads
- Heavy server load

## Next Steps

### 1. First Successful Run

After your first successful login:

- Check `screenshots/` for visual confirmation
- Review `logs/` for execution details
- Verify you see "Login successful!" in console

### 2. Understanding the Output

**Console logs show:**
```
2025-11-08 10:30:00 - INFO - Setting up browser...
2025-11-08 10:30:02 - INFO - Navigating to LinkedIn...
2025-11-08 10:30:05 - INFO - Entering email...
2025-11-08 10:30:08 - INFO - Entering password...
2025-11-08 10:30:12 - INFO - Clicking login button...
2025-11-08 10:30:15 - INFO - Login successful!
```

**Screenshot files:**
```
01_login_page_20251108_103000.png
02_credentials_entered_20251108_103010.png
03_login_success_20251108_103015.png
```

### 3. Explore the Code

**Key files to understand:**
1. `linkedin_login_bot.py` - Main bot logic
2. `.env` - Your configuration
3. `check_setup.py` - Verification script

**Read the docs:**
- [START_HERE.md](START_HERE.md) - Project overview and learning path
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Architecture details
- [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) - Testing guide

### 4. Customize Behavior

**Change typing speed:**

Edit `linkedin_login_bot.py`, find this line:
```python
await element.type(char, delay=random.randint(50, 150))
```

Make it faster:
```python
await element.type(char, delay=random.randint(30, 80))
```

Make it slower (more human-like):
```python
await element.type(char, delay=random.randint(100, 250))
```

**Change random delays:**

Find:
```python
await self.human_delay(1000, 8000)
```

Adjust min/max (in milliseconds):
```python
await self.human_delay(500, 3000)  # Faster
await self.human_delay(2000, 10000)  # Slower
```

## Best Practices

### For Testing

1. **Use a test account first**
   - Create separate LinkedIn account
   - Don't risk your main account
   - Easier to test with

2. **Start visible (non-headless)**
   ```env
   HEADLESS_MODE=false
   ```
   - See what's happening
   - Easier to debug
   - Can intervene if needed

3. **Run verification before each session**
   ```bash
   python check_setup.py && python linkedin_login_bot.py
   ```

### For Safety

1. **Limit frequency**
   - Max 3-5 runs per day
   - Add delays between runs
   - Monitor for warnings

2. **Monitor LinkedIn emails**
   - Check for security alerts
   - Respond to verification requests
   - Watch for account warnings

3. **Keep screenshots**
   - Don't delete `screenshots/` folder
   - Useful for debugging
   - Evidence if account issues arise

### For Development

1. **Enable debug logging**
   ```env
   LOG_LEVEL=DEBUG
   ```

2. **Read the logs**
   ```bash
   tail -f logs/linkedin_bot_*.log
   ```

3. **Test incrementally**
   - Make small changes
   - Test after each change
   - Keep working versions

## Common Commands Cheat Sheet

```bash
# Install everything
pip install -r requirements.txt && playwright install chromium

# Setup config
cp .env.example .env && nano .env

# Verify setup
python check_setup.py

# Run bot
python linkedin_login_bot.py

# Check logs
cat logs/linkedin_bot_*.log

# View latest screenshots
ls -lt screenshots/ | head -n 5

# Clean up old logs (optional)
rm logs/*.log

# Clean up old screenshots (optional)
rm screenshots/*.png

# Check Python version
python --version

# Check installed packages
pip list | grep -E 'playwright|dotenv|colorlog|pytest'
```

## Getting Help

### Check These First

1. **Error messages** - Read them carefully
2. **Logs** - Check `logs/` directory
3. **Screenshots** - Check `screenshots/` directory
4. **Documentation** - Review other .md files

### Still Stuck?

1. Run setup verification:
   ```bash
   python check_setup.py
   ```

2. Enable debug mode in `.env`:
   ```env
   LOG_LEVEL=DEBUG
   ```

3. Check the full README:
   - [README.md](README.md) - Comprehensive documentation

4. Review project structure:
   - [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## Success Checklist

- [ ] All dependencies installed
- [ ] Playwright browsers downloaded
- [ ] `.env` file created and configured
- [ ] `check_setup.py` passes all checks
- [ ] Bot logs in successfully
- [ ] Screenshots captured
- [ ] Logs created
- [ ] Understand basic configuration
- [ ] Know where to find help

## What's Next?

1. **Experiment** - Try different configurations
2. **Learn** - Read [START_HERE.md](START_HERE.md) for the full roadmap
3. **Build** - Extend the bot with new features
4. **Test** - Follow [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)

**Happy automating!**
