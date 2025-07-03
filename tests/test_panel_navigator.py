#!/usr/bin/env python3
"""Tests for the panel navigator module."""

import os
import sys
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panel_navigator import PanelNavigator


class TestPanelNavigator:
    """Test cases for the PanelNavigator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {"grafana_kiosk_mode": True}
        self.navigator = PanelNavigator(self.config)

    def test_prepare_panel_url_basic(self):
        """Test basic URL preparation with kiosk mode enabled."""
        url = "http://localhost:3000/d/test"
        prepared_url = self.navigator._prepare_panel_url(url)
        assert prepared_url == "http://localhost:3000/d/test?kiosk"

    def test_prepare_panel_url_with_existing_params(self):
        """Test URL preparation with existing parameters."""
        url = "http://localhost:3000/d/test?orgId=1&refresh=5s"
        prepared_url = self.navigator._prepare_panel_url(url)
        assert prepared_url == "http://localhost:3000/d/test?orgId=1&refresh=5s&kiosk"

    def test_prepare_panel_url_already_has_kiosk(self):
        """Test URL preparation when kiosk parameter already exists."""
        url = "http://localhost:3000/d/test?kiosk"
        prepared_url = self.navigator._prepare_panel_url(url)
        assert prepared_url == "http://localhost:3000/d/test?kiosk"

        url = "http://localhost:3000/d/test?orgId=1&kiosk&refresh=5s"
        prepared_url = self.navigator._prepare_panel_url(url)
        assert prepared_url == "http://localhost:3000/d/test?orgId=1&kiosk&refresh=5s"

    def test_prepare_panel_url_disabled(self):
        """Test URL preparation with kiosk mode disabled."""
        config = {"grafana_kiosk_mode": False}
        navigator = PanelNavigator(config)

        url = "http://localhost:3000/d/test"
        prepared_url = navigator._prepare_panel_url(url)
        assert prepared_url == "http://localhost:3000/d/test"

    def test_prepare_panel_url_with_fragment(self):
        """Test URL preparation with fragments."""
        url = "http://localhost:3000/d/test#section"
        prepared_url = self.navigator._prepare_panel_url(url)
        assert prepared_url == "http://localhost:3000/d/test?kiosk#section"

        url = "http://localhost:3000/d/test?orgId=1#section"
        prepared_url = self.navigator._prepare_panel_url(url)
        assert prepared_url == "http://localhost:3000/d/test?orgId=1&kiosk#section"

    def test_prepare_panel_url_default_behavior(self):
        """Test URL preparation with default configuration (no grafana_kiosk_mode specified)."""
        config = {}  # No grafana_kiosk_mode specified
        navigator = PanelNavigator(config)

        url = "http://localhost:3000/d/test"
        prepared_url = navigator._prepare_panel_url(url)
        assert (
            prepared_url == "http://localhost:3000/d/test?kiosk"
        )  # Should default to True

    @patch("panel_navigator.WebDriverWait")
    def test_navigate_to_panel_url_modification(self, mock_wait):
        """Test that navigate_to_panel properly modifies URLs."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "complete"
        mock_wait.return_value.until.return_value = True

        panel = {"name": "Test Panel", "url": "http://localhost:3000/d/test?orgId=1"}

        result = self.navigator.navigate_to_panel(mock_driver, panel)

        assert result is True
        # Verify that the URL was modified to include kiosk parameter
        mock_driver.get.assert_called_once_with(
            "http://localhost:3000/d/test?orgId=1&kiosk"
        )

    @patch("panel_navigator.WebDriverWait")
    def test_navigate_to_panel_with_auth_handler(self, mock_wait):
        """Test navigate_to_panel with authentication handler."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "complete"
        mock_wait.return_value.until.return_value = True

        mock_auth_handler = Mock()
        mock_auth_handler.check_and_handle_authentication.return_value = True

        panel = {"name": "Test Panel", "url": "http://localhost:3000/d/test"}

        result = self.navigator.navigate_to_panel(mock_driver, panel, mock_auth_handler)

        assert result is True
        mock_driver.get.assert_called_once_with("http://localhost:3000/d/test?kiosk")
        mock_auth_handler.check_and_handle_authentication.assert_called_once_with(
            mock_driver
        )

    @patch("panel_navigator.WebDriverWait")
    def test_navigate_to_panel_auth_failure(self, mock_wait):
        """Test navigate_to_panel when authentication fails."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "complete"
        mock_wait.return_value.until.return_value = True

        mock_auth_handler = Mock()
        mock_auth_handler.check_and_handle_authentication.return_value = False

        panel = {"name": "Test Panel", "url": "http://localhost:3000/d/test"}

        result = self.navigator.navigate_to_panel(mock_driver, panel, mock_auth_handler)

        assert result is False
        mock_driver.get.assert_called_once_with("http://localhost:3000/d/test?kiosk")
        mock_auth_handler.check_and_handle_authentication.assert_called_once_with(
            mock_driver
        )
