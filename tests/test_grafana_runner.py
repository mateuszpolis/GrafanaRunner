"""Tests for the Grafana Runner application."""

import json
import os
import sys
import tempfile
from unittest.mock import Mock, patch

import pytest

# Add the parent directory to the path so we can import grafana_runner
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grafana_runner import GrafanaRunner  # noqa: E402


class TestGrafanaRunner:
    """Test cases for GrafanaRunner class."""

    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test?kiosk",
                    "duration": 10,
                }
            ],
            "browser_settings": {"browser": "chrome", "fullscreen": True},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)
            assert runner.config["panels"][0]["name"] == "Test Panel"
            assert runner.config["browser_settings"]["browser"] == "chrome"
        finally:
            os.unlink(config_path)

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

    def test_create_default_config(self):
        """Test creation of default configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")

            GrafanaRunner(config_path)

            # Should create default config
            assert os.path.exists(config_path)

            with open(config_path, "r") as f:
                config = json.load(f)

            assert "panels" in config
            assert "browser_settings" in config
            assert len(config["panels"]) > 0

    @patch("grafana_runner.webdriver.Chrome")
    def test_setup_chrome_browser(self, mock_chrome):
        """Test Chrome browser setup."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test?kiosk",
                    "duration": 10,
                }
            ],
            "browser_settings": {
                "browser": "chrome",
                "fullscreen": True,
                "disable_extensions": True,
                "incognito": True,
                "page_load_timeout": 30,
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            mock_driver = Mock()
            mock_chrome.return_value = mock_driver

            runner.setup_browser()

            # Verify Chrome was called
            mock_chrome.assert_called_once()

            # Verify driver methods were called
            mock_driver.set_page_load_timeout.assert_called_with(30)
            mock_driver.implicitly_wait.assert_called_with(10)

            assert runner.driver == mock_driver

        finally:
            os.unlink(config_path)

    def test_cleanup(self):
        """Test cleanup method."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test?kiosk",
                    "duration": 10,
                }
            ],
            "browser_settings": {"browser": "chrome"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            # Mock a driver
            mock_driver = Mock()
            runner.driver = mock_driver

            runner.cleanup()

            # Verify driver.quit() was called
            mock_driver.quit.assert_called_once()

        finally:
            os.unlink(config_path)
