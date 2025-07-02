"""Tests for browser setup and SSL functionality."""

import json
import os
import sys
import tempfile
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import grafana_runner
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grafana_runner import GrafanaRunner  # noqa: E402


class TestBrowserSetup:
    """Test cases for browser setup functionality."""

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

    @patch("grafana_runner.webdriver.Chrome")
    def test_setup_chrome_with_ssl_bypass(self, mock_chrome):
        """Test Chrome browser setup with SSL certificate bypass enabled."""
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
                "disable_extensions": True,
                "ignore_ssl_errors": True,
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

            # We need to mock the ChromeOptions to inspect the arguments
            with patch("grafana_runner.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_options.arguments = []

                # Mock the add_argument method to track calls
                def add_argument_side_effect(arg):
                    mock_options.arguments.append(arg)

                mock_options.add_argument.side_effect = add_argument_side_effect

                runner.setup_browser()

                # Verify Chrome was called with options
                mock_chrome.assert_called_once()

                # Check that SSL bypass arguments were added
                expected_ssl_args = [
                    "--ignore-certificate-errors",
                    "--ignore-ssl-errors",
                    "--ignore-certificate-errors-spki-list",
                    "--allow-running-insecure-content",
                    "--disable-web-security",
                    "--allow-insecure-localhost",
                    "--test-type",
                ]

                for expected_arg in expected_ssl_args:
                    assert (
                        expected_arg in mock_options.arguments
                    ), f"Expected SSL bypass argument {expected_arg} not found in Chrome options"

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Chrome")
    def test_setup_chrome_without_ssl_bypass(self, mock_chrome):
        """Test Chrome browser setup with SSL certificate bypass disabled."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "https://secure-site.com/d/test?kiosk",
                    "duration": 10,
                }
            ],
            "browser_settings": {
                "browser": "chrome",
                "fullscreen": True,
                "disable_extensions": True,
                "ignore_ssl_errors": False,
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

            # We need to mock the ChromeOptions to inspect the arguments
            with patch("grafana_runner.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_options.arguments = []

                # Mock the add_argument method to track calls
                def add_argument_side_effect(arg):
                    mock_options.arguments.append(arg)

                mock_options.add_argument.side_effect = add_argument_side_effect

                runner.setup_browser()

                # Verify Chrome was called
                mock_chrome.assert_called_once()

                # Check that SSL bypass arguments are NOT present
                ssl_specific_args = [
                    "--ignore-certificate-errors",
                    "--ignore-ssl-errors",
                    "--ignore-certificate-errors-spki-list",
                    "--allow-running-insecure-content",
                    "--allow-insecure-localhost",
                    "--test-type",
                ]

                for ssl_arg in ssl_specific_args:
                    assert (
                        ssl_arg not in mock_options.arguments
                    ), f"SSL bypass argument {ssl_arg} should not be present when ignore_ssl_errors is False"

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Chrome")
    def test_ssl_bypass_default_behavior(self, mock_chrome):
        """Test that SSL bypass is enabled by default when ignore_ssl_errors is not specified."""
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
                # Note: ignore_ssl_errors not specified, should default to True
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            mock_driver = Mock()
            mock_chrome.return_value = mock_driver

            # We need to mock the ChromeOptions to inspect the arguments
            with patch("grafana_runner.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_options.arguments = []

                # Mock the add_argument method to track calls
                def add_argument_side_effect(arg):
                    mock_options.arguments.append(arg)

                mock_options.add_argument.side_effect = add_argument_side_effect

                runner.setup_browser()

                # Verify Chrome was called
                mock_chrome.assert_called_once()

                # Since ignore_ssl_errors defaults to True, SSL bypass arguments should be present
                assert "--ignore-certificate-errors" in mock_options.arguments
                assert "--ignore-ssl-errors" in mock_options.arguments

        finally:
            os.unlink(config_path)
