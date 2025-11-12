"""Unit tests for helper utilities."""

import pytest

from src.utils.helpers import (
    generate_random_user_agent,
    generate_realistic_viewport,
)


@pytest.mark.unit
class TestHelpers:
    """Test helper utility functions."""

    def test_generate_realistic_viewport(self):
        """Test viewport generation."""
        viewport = generate_realistic_viewport()

        assert isinstance(viewport, dict)
        assert "width" in viewport
        assert "height" in viewport
        assert viewport["width"] > 0
        assert viewport["height"] > 0

    def test_generate_random_user_agent(self):
        """Test user agent generation."""
        user_agent = generate_random_user_agent()

        assert isinstance(user_agent, str)
        assert "Mozilla" in user_agent
        assert "Chrome" in user_agent
