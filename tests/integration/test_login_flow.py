"""Integration tests for login flow."""

import pytest

from src.pages.login_page import LoginPage


@pytest.mark.integration
@pytest.mark.requires_browser
class TestLoginFlow:
    """Test login page flow."""

    @pytest.mark.asyncio
    async def test_login_page_loads(self, page):
        """Test that login page loads correctly."""
        login_page = LoginPage(page)
        await login_page.navigate()

        loaded = await login_page.verify_loaded()
        assert loaded is True

    @pytest.mark.asyncio
    async def test_login_page_url(self, page):
        """Test login page URL."""
        login_page = LoginPage(page)
        expected_url = login_page.get_url()

        assert "linkedin.com/login" in expected_url
