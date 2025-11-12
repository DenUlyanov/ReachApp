"""End-to-end tests for full bot workflows."""

import pytest

from src.bot.linkedin_bot import LinkedInBot


@pytest.mark.e2e
@pytest.mark.slow
class TestFullBot:
    """Test complete bot workflows."""

    @pytest.mark.asyncio
    async def test_bot_initialization(self):
        """Test bot can be initialized."""
        async with LinkedInBot() as bot:
            assert bot is not None
            assert bot.browser_manager is not None

    @pytest.mark.asyncio
    @pytest.mark.requires_credentials
    async def test_health_check(self):
        """Test bot health check."""
        async with LinkedInBot() as bot:
            # Health check should work even without credentials
            health = await bot.run_health_check()

            assert isinstance(health, dict)
            assert "browser_initialized" in health
