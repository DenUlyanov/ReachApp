# Architecture Documentation

This document provides a comprehensive overview of the LinkedIn Lead Bot's architecture, design patterns, and implementation details.

## Table of Contents

- [System Overview](#system-overview)
- [Design Patterns](#design-patterns)
- [Module Architecture](#module-architecture)
- [Class Diagrams](#class-diagrams)
- [Data Flow](#data-flow)
- [Best Practices](#best-practices)

## System Overview

The LinkedIn Lead Bot is built following modern software engineering principles with a focus on maintainability, testability, and extensibility.

### Core Principles

1. **Separation of Concerns** - Each module has a single responsibility
2. **DRY (Don't Repeat Yourself)** - No code duplication
3. **SOLID Principles** - Object-oriented design patterns
4. **Type Safety** - Full type hints throughout
5. **Async First** - All I/O operations are asynchronous
6. **Configuration Over Code** - Externalized configuration

### Technology Stack

- **Python 3.11+** - Modern Python features
- **Playwright** - Browser automation
- **Pydantic** - Data validation and settings
- **PyYAML** - Configuration management
- **Pytest** - Testing framework
- **Colorlog** - Structured logging

## Design Patterns

### 1. Singleton Pattern

**Used in:** `BrowserManager`, `BotLogger`, `ScreenshotManager`

**Purpose:** Ensure only one instance exists

```
┌─────────────────────┐
│  BrowserManager     │
│  ┌──────────────┐   │
│  │  _instance   │───┼──► Single shared instance
│  └──────────────┘   │
│                     │
│  get_instance()     │
│  initialize()       │
│  get_page()         │
│  close()            │
└─────────────────────┘
```

**Why:** Browser instances are expensive to create. Singleton ensures we reuse the same browser throughout the session.

### 2. Page Object Model (POM)

**Used in:** All page classes (`LoginPage`, `FeedPage`, `SalesNavigatorPage`)

**Purpose:** Encapsulate page-specific logic

```
┌──────────────┐
│   BasePage   │ (Abstract)
└──────────────┘
       △
       │ inherits
       │
   ┌───┴───┬────────┬──────────────┐
   │       │        │              │
┌──┴──┐ ┌─┴──┐  ┌──┴───┐  ┌──────┴────────┐
│Login│ │Feed│  │Sales │  │  Future Pages │
│Page │ │Page│  │  Nav │  │               │
└─────┘ └────┘  └──────┘  └───────────────┘
```

**Benefits:**
- Page logic separated from tests
- Easy to maintain when UI changes
- Reusable page methods
- Clear API for each page

### 3. Factory Pattern

**Used in:** Page object creation

**Purpose:** Centralize object instantiation

```python
# Factory-like creation in LinkedInBot
async def initialize(self):
    page = await self.browser_manager.get_page()

    self.login_page = LoginPage(page)
    self.feed_page = FeedPage(page)
    self.sales_nav_page = SalesNavigatorPage(page)
```

### 4. Strategy Pattern

**Used in:** Configurable behavior (delays, user agents)

**Purpose:** Make algorithms interchangeable

```
┌─────────────────────┐
│   Settings          │
│  ┌──────────────┐   │
│  │ delays       │   │◄─── YAML config
│  │ browser      │   │
│  │ timeouts     │   │
│  └──────────────┘   │
└─────────────────────┘
         │
         │ provides
         ▼
┌─────────────────────┐
│  Runtime Behavior   │
│  - Typing speed     │
│  - Delays           │
│  - User agent       │
└─────────────────────┘
```

### 5. Observer Pattern

**Used in:** Logging system

**Purpose:** Notify multiple handlers of events

```
┌─────────┐     logs to    ┌──────────────┐
│  Code   │───────────────►│   Logger     │
└─────────┘                └──────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
             ┌──────▼──────┐           ┌───────▼──────┐
             │   Console   │           │   File       │
             │   Handler   │           │   Handler    │
             └─────────────┘           └──────────────┘
```

### 6. Context Manager Pattern

**Used in:** `BrowserManager`, `LinkedInBot`

**Purpose:** Resource management (RAII)

```python
async with LinkedInBot() as bot:
    await bot.login()
    # Browser automatically closed on exit
```

## Module Architecture

### 1. Configuration Layer (`src/config/`)

**Responsibility:** Manage all configuration

```
┌─────────────────────────────────────┐
│         Configuration Layer          │
├─────────────────────────────────────┤
│  settings.py                         │
│   - Pydantic models                  │
│   - Environment variables            │
│   - YAML loading                     │
│                                      │
│  constants.py                        │
│   - Global constants                 │
│   - URLs, timeouts, paths            │
└─────────────────────────────────────┘
```

**Key Classes:**
- `Settings` - Pydantic BaseSettings with validation
- `get_settings()` - Singleton accessor

### 2. Core Layer (`src/core/`)

**Responsibility:** Foundation classes

```
┌─────────────────────────────────────┐
│            Core Layer                │
├─────────────────────────────────────┤
│  browser_manager.py                  │
│   - Singleton browser instance       │
│   - Anti-detection setup             │
│   - Page creation                    │
│                                      │
│  base_page.py                        │
│   - Abstract base for pages          │
│   - Common page operations           │
│   - Human-like behavior              │
└─────────────────────────────────────┘
```

**Key Classes:**
- `BrowserManager` - Singleton, manages browser lifecycle
- `BasePage` - Abstract, defines page interface

### 3. Pages Layer (`src/pages/`)

**Responsibility:** Page-specific logic

```
┌─────────────────────────────────────┐
│           Pages Layer                │
├─────────────────────────────────────┤
│  login_page.py                       │
│   - Login workflow                   │
│   - Challenge detection              │
│                                      │
│  feed_page.py                        │
│   - Feed interactions                │
│   - Content browsing                 │
│                                      │
│  sales_navigator_page.py             │
│   - Company search                   │
│   - Lead generation                  │
└─────────────────────────────────────┘
```

**Each page implements:**
- `get_url()` - Page URL
- `verify_loaded()` - Load verification
- Page-specific methods

### 4. Utilities Layer (`src/utils/`)

**Responsibility:** Reusable utilities

```
┌─────────────────────────────────────┐
│          Utilities Layer             │
├─────────────────────────────────────┤
│  logger.py                           │
│   - Centralized logging              │
│   - File rotation                    │
│                                      │
│  helpers.py                          │
│   - Human-like behavior              │
│   - Retry decorators                 │
│                                      │
│  screenshot_manager.py               │
│   - Screenshot capture               │
│   - Organization by session          │
└─────────────────────────────────────┘
```

### 5. Bot Layer (`src/bot/`)

**Responsibility:** Orchestration

```
┌─────────────────────────────────────┐
│             Bot Layer                │
├─────────────────────────────────────┤
│  linkedin_bot.py                     │
│   - Main orchestrator                │
│   - Workflow coordination            │
│   - Page management                  │
│   - Error handling                   │
└─────────────────────────────────────┘
```

**Key Class:**
- `LinkedInBot` - Coordinates all operations

### 6. Exceptions Layer (`src/exceptions.py`)

**Responsibility:** Custom error types

```
LinkedInBotException (base)
    │
    ├── LoginFailedException
    ├── CaptchaDetectedException
    ├── TwoFactorRequiredException
    ├── UnusualActivityException
    ├── NavigationException
    ├── ElementNotFoundException
    ├── BrowserInitializationException
    ├── ConfigurationException
    └── TimeoutException
```

## Class Diagrams

### Complete System Overview (ASCII)

```
┌───────────────────────────────────────────────────────────────┐
│                     LinkedIn Bot System                        │
└───────────────────────────────────────────────────────────────┘
                               │
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  LinkedInBot │      │    Config    │      │   Utilities  │
│              │      │              │      │              │
│ - browser_   │      │ - Settings   │      │ - Logger     │
│   manager    │      │ - Constants  │      │ - Helpers    │
│ - pages      │      │              │      │ - Screenshot │
│              │      │              │      │              │
│ + login()    │      │ + get_       │      │ + get_logger │
│ + navigate() │      │   settings() │      │ + random_    │
└──────┬───────┘      └──────────────┘      │   delay()    │
       │                                     └──────────────┘
       │ uses
       │
       ▼
┌──────────────┐
│ Browser      │
│ Manager      │◄────────────┐
│              │             │
│ - _instance  │             │
│ - browser    │             │
│ - context    │             │
│              │             │ creates
│ + get_page() │             │
└──────┬───────┘             │
       │                     │
       │ provides            │
       │                     │
       ▼                     │
┌──────────────┐      ┌──────┴───────┐
│     Page     │      │   BasePage   │
│   (Playwright)│─────►│  (Abstract)  │
└──────────────┘      └──────┬───────┘
                             │
                             │ inherited by
                ┌────────────┼────────────┐
                │            │            │
         ┌──────▼──────┐ ┌──▼──────┐ ┌──▼────────┐
         │  LoginPage  │ │FeedPage │ │  SalesNav │
         │             │ │         │ │   Page    │
         │ + login()   │ │+ scroll()│ │+ search() │
         └─────────────┘ └─────────┘ └───────────┘
```

### BrowserManager Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                  Browser Lifecycle                       │
└─────────────────────────────────────────────────────────┘

1. Initialization:
   get_instance() ─► BrowserManager (singleton)
                         │
                         ▼
                    initialize()
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  Start Playwright  Launch Browser  Create Context
        │                │                │
        └────────────────┴────────────────┘
                         │
                         ▼
                   Inject Stealth
                         │
                         ▼
                    Create Page
                         │
                         ▼
                   [Ready for use]

2. Usage:
   get_page() ─► Returns Page instance
   new_page() ─► Creates additional page

3. Cleanup:
   close() ─► Closes all resources
```

### Login Flow Sequence

```
User Code                 LinkedInBot           LoginPage          BrowserManager
    │                          │                    │                    │
    ├──login()────────────────►│                    │                    │
    │                          ├──initialize()──────┼───────────────────►│
    │                          │                    │                    │
    │                          │◄───────────────────┼────────────────────┤
    │                          │                    │       page         │
    │                          ├──LoginPage(page)──►│                    │
    │                          │                    │                    │
    │                          ├──login()──────────►│                    │
    │                          │                    ├──navigate()        │
    │                          │                    ├──enter_email()     │
    │                          │                    ├──enter_password()  │
    │                          │                    ├──click_sign_in()   │
    │                          │                    ├──detect_challenges()│
    │                          │                    ├──verify_success()  │
    │                          │◄───────────────────┤                    │
    │◄─────────────────────────┤      result        │                    │
    │                          │                    │                    │
```

## Data Flow

### Configuration Loading

```
┌─────────┐
│  .env   │────┐
└─────────┘    │
               │
┌─────────┐    │    ┌──────────────┐
│settings.│────┼───►│   Settings   │
│ yaml    │    │    │   (Pydantic) │
└─────────┘    │    └──────┬───────┘
               │           │
┌─────────┐    │           │ provides config
│selectors│────┘           │
│ .yaml   │                │
└─────────┘                ▼
                    ┌─────────────┐
                    │ Application │
                    └─────────────┘
```

### Request Flow

```
User Request
    │
    ▼
LinkedInBot.login()
    │
    ├─► BrowserManager.get_page()
    │        │
    │        └─► Page instance
    │
    ├─► LoginPage(page)
    │        │
    │        ├─► navigate()
    │        │     └─► helpers.random_delay()
    │        │
    │        ├─► enter_email()
    │        │     └─► helpers.human_type()
    │        │
    │        ├─► enter_password()
    │        │     └─► helpers.human_type()
    │        │
    │        ├─► click_sign_in()
    │        │     └─► helpers.random_mouse_move()
    │        │
    │        └─► detect_security_challenge()
    │              │
    │              ├─► is_captcha_present()
    │              ├─► is_2fa_present()
    │              └─► detect_unusual_activity()
    │
    └─► Result (bool)
```

## Best Practices

### 1. Adding New Features

**DO:**
✅ Create new page objects for new pages
✅ Add selectors to `selectors.yaml`
✅ Write tests for new functionality
✅ Use type hints
✅ Add docstrings

**DON'T:**
❌ Hardcode selectors in code
❌ Skip tests
❌ Ignore type hints
❌ Mix concerns

### 2. Error Handling

```python
# Good: Specific exceptions
try:
    await bot.login()
except CaptchaDetectedException as e:
    handle_captcha()
except LoginFailedException as e:
    handle_login_failure()

# Bad: Generic exceptions
try:
    await bot.login()
except Exception as e:
    # Too broad!
    pass
```

### 3. Configuration

```python
# Good: Use settings
settings = get_settings()
delay = settings.get_delay_config()

# Bad: Hardcode
await asyncio.sleep(2)  # Magic number!
```

### 4. Logging

```python
# Good: Structured logging
logger.info(f"Logging in with email: {email[:3]}***")
logger.debug(f"Delay: {delay:.2f}s")

# Bad: Print statements
print("Logging in...")  # No!
```

### 5. Testing

```python
# Good: Test through interfaces
@pytest.mark.asyncio
async def test_login(mock_page):
    login_page = LoginPage(mock_page)
    result = await login_page.verify_loaded()
    assert result is True

# Bad: Test implementation details
# Don't test private methods or internals
```

## Scalability Considerations

### Horizontal Scaling

The framework supports running multiple bot instances:

```python
# Multiple bots in parallel
async def run_multiple_bots():
    tasks = []
    for credentials in credential_list:
        bot = LinkedInBot()
        task = bot.login(**credentials)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
```

### Performance Optimization

1. **Connection Pooling** - Reuse browser contexts
2. **Lazy Loading** - Initialize pages only when needed
3. **Caching** - Cache settings and selectors
4. **Async Operations** - Non-blocking I/O throughout

## Conclusion

This architecture provides:

- ✅ **Maintainability** - Easy to understand and modify
- ✅ **Testability** - Comprehensive test coverage
- ✅ **Extensibility** - Easy to add new features
- ✅ **Reliability** - Robust error handling
- ✅ **Performance** - Async operations throughout
- ✅ **Type Safety** - Full type hints
- ✅ **Documentation** - Well-documented codebase

The design follows industry best practices and modern Python patterns, making it production-ready and enterprise-grade.
