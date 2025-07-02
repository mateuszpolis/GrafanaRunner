"""Tests for configuration validation functionality."""

import os
import sys

import pytest

# Add the parent directory to the path so we can import grafana_runner
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grafana_runner import GrafanaRunner  # noqa: E402


class TestConfigurationValidation:
    """Test cases for configuration validation."""

    def test_validate_config_missing_panels(self):
        """Test validation with missing panels key."""
        config_data = {"browser_settings": {"browser": "chrome"}}

        runner = GrafanaRunner()
        with pytest.raises(ValueError, match="Missing required config key: panels"):
            runner.validate_config(config_data)

    def test_validate_config_missing_browser_settings(self):
        """Test validation with missing browser_settings key."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test?kiosk",
                    "duration": 10,
                }
            ]
        }

        runner = GrafanaRunner()
        with pytest.raises(
            ValueError, match="Missing required config key: browser_settings"
        ):
            runner.validate_config(config_data)

    def test_validate_config_empty_panels(self):
        """Test validation with empty panels array."""
        config_data = {"panels": [], "browser_settings": {"browser": "chrome"}}

        runner = GrafanaRunner()
        with pytest.raises(ValueError, match="No panels configured"):
            runner.validate_config(config_data)

    def test_validate_config_panel_missing_url(self):
        """Test validation with panel missing URL."""
        config_data = {
            "panels": [{"name": "Test Panel", "duration": 10}],
            "browser_settings": {"browser": "chrome"},
        }

        runner = GrafanaRunner()
        with pytest.raises(ValueError, match="Panel 0 missing URL"):
            runner.validate_config(config_data)

    def test_validate_config_panel_missing_duration(self):
        """Test validation with panel missing duration."""
        config_data = {
            "panels": [
                {"name": "Test Panel", "url": "http://localhost:3000/d/test?kiosk"}
            ],
            "browser_settings": {"browser": "chrome"},
        }

        runner = GrafanaRunner()
        with pytest.raises(ValueError, match="Panel 0 missing duration"):
            runner.validate_config(config_data)

    def test_validate_config_with_ssl_settings(self):
        """Test that configuration validation works with SSL settings."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "https://agrana.cern.ch/d/test?kiosk",
                    "duration": 10,
                }
            ],
            "browser_settings": {
                "browser": "chrome",
                "fullscreen": True,
                "ignore_ssl_errors": True,
                "disable_web_security": False,
            },
        }

        runner = GrafanaRunner()
        # Should not raise any exception
        runner.validate_config(config_data)

        # Test that the config is properly loaded
        assert config_data["browser_settings"]["ignore_ssl_errors"] is True
        assert config_data["browser_settings"]["disable_web_security"] is False
