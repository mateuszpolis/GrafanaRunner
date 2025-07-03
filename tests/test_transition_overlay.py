#!/usr/bin/env python3
"""Tests for transition overlay functionality."""

import os
import sys
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panel_navigator import PanelNavigator


class TestTransitionOverlay:
    """Test cases for transition overlay functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {"grafana_kiosk_mode": True}
        self.navigator = PanelNavigator(self.config)

    def test_show_transition_overlay_basic(self):
        """Test basic transition overlay display."""
        mock_driver = Mock()

        previous_panel = {"name": "Previous Panel", "duration": 10}

        current_panel = {"name": "Current Panel", "duration": 15}

        # Should not raise an exception
        self.navigator.show_transition_overlay(
            mock_driver, previous_panel, current_panel
        )

        # Verify JavaScript was executed
        mock_driver.execute_script.assert_called_once()

        # Check that the executed script contains panel names
        executed_script = mock_driver.execute_script.call_args[0][0]
        assert "Previous Panel" in executed_script
        assert "Current Panel" in executed_script

    def test_show_transition_overlay_with_variables(self):
        """Test transition overlay with panel variables."""
        mock_driver = Mock()

        previous_panel = {
            "name": "Previous Panel",
            "duration": 10,
            "variables": {"param": "value1", "region": "us-east"},
        }

        current_panel = {
            "name": "Current Panel",
            "duration": 15,
            "variables": {"param": "value2", "environment": "production"},
        }

        # Should not raise an exception
        self.navigator.show_transition_overlay(
            mock_driver, previous_panel, current_panel
        )

        # Verify JavaScript was executed
        mock_driver.execute_script.assert_called_once()

        # Check that the executed script contains variable information
        executed_script = mock_driver.execute_script.call_args[0][0]
        assert "param=value1" in executed_script
        assert "region=us-east" in executed_script
        assert "param=value2" in executed_script
        assert "environment=production" in executed_script

    def test_show_transition_overlay_no_previous_panel(self):
        """Test transition overlay when there's no previous panel (first panel)."""
        mock_driver = Mock()

        current_panel = {"name": "First Panel", "duration": 10}

        # Should not raise an exception
        self.navigator.show_transition_overlay(mock_driver, None, current_panel)

        # Verify JavaScript was executed
        mock_driver.execute_script.assert_called_once()

        # Check that "Starting" appears for previous panel
        executed_script = mock_driver.execute_script.call_args[0][0]
        assert "Starting" in executed_script
        assert "First Panel" in executed_script

    def test_hide_transition_overlay(self):
        """Test hiding the transition overlay."""
        mock_driver = Mock()

        # Should not raise an exception
        self.navigator.hide_transition_overlay(mock_driver)

        # Verify JavaScript was executed
        mock_driver.execute_script.assert_called_once()

        # Check that the script contains overlay removal logic
        executed_script = mock_driver.execute_script.call_args[0][0]
        assert "kiosk-transition-overlay" in executed_script
        assert "fadeOut" in executed_script

    def test_format_variables_simple(self):
        """Test variable formatting for simple variables."""
        panel = {"variables": {"param": "value1", "region": "us-east"}}

        result = self.navigator._format_variables(panel)
        assert "param=value1" in result
        assert "region=us-east" in result

    def test_format_variables_list_short(self):
        """Test variable formatting for short lists."""
        panel = {"variables": {"params": ["value1", "value2"]}}

        result = self.navigator._format_variables(panel)
        assert "params=[value1, value2]" in result

    def test_format_variables_list_long(self):
        """Test variable formatting for long lists."""
        panel = {
            "variables": {"params": ["value1", "value2", "value3", "value4", "value5"]}
        }

        result = self.navigator._format_variables(panel)
        assert "params=[5 values]" in result

    def test_format_variables_empty(self):
        """Test variable formatting for panel without variables."""
        panel = {}
        result = self.navigator._format_variables(panel)
        assert result == ""

        panel = {"variables": {}}
        result = self.navigator._format_variables(panel)
        assert result == ""

    def test_navigate_to_panel_with_transition(self):
        """Test that navigate_to_panel properly shows and hides overlay."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "complete"

        with patch("panel_navigator.WebDriverWait") as mock_wait:
            mock_wait_instance = Mock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.return_value = True

            with patch("panel_navigator.time.sleep") as mock_sleep:
                previous_panel = {"name": "Previous", "duration": 10}
                current_panel = {
                    "name": "Current",
                    "url": "http://test.com",
                    "duration": 15,
                }

                result = self.navigator.navigate_to_panel(
                    mock_driver, current_panel, previous_panel=previous_panel
                )

                assert result is True

                # Should be called at least once to show overlay
                assert mock_driver.execute_script.call_count >= 1

                # Should sleep for overlay duration and Grafana rendering
                assert mock_sleep.call_count >= 2

    def test_minimum_overlay_duration(self):
        """Test that overlay is displayed for minimum duration before navigation."""
        config = {"grafana_kiosk_mode": True, "transition_overlay_min_duration": 1.5}
        navigator = PanelNavigator(config)
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "complete"

        with patch("panel_navigator.WebDriverWait") as mock_wait:
            mock_wait_instance = Mock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.return_value = True

            with patch("panel_navigator.time.sleep") as mock_sleep:
                current_panel = {
                    "name": "Test",
                    "url": "http://test.com",
                    "duration": 10,
                }

                result = navigator.navigate_to_panel(mock_driver, current_panel)

                assert result is True

                # Should sleep for:
                # 1. Minimum overlay duration (1.5s) - BEFORE navigation
                # 2. Grafana rendering (3s) - AFTER navigation
                sleep_calls = mock_sleep.call_args_list
                sleep_times = [call[0][0] for call in sleep_calls]

                # Should include the 1.5s overlay time and 3s Grafana wait
                assert 1.5 in sleep_times
                assert 3.0 in sleep_times

                # Verify overlay is shown and navigation happens in correct order
                assert mock_driver.execute_script.call_count >= 1  # Show overlay
                assert mock_driver.get.call_count == 1  # Navigate once

    def test_overlay_exception_handling(self):
        """Test that exceptions in overlay methods don't break navigation."""
        mock_driver = Mock()
        mock_driver.execute_script.side_effect = Exception("JS Error")

        with patch("panel_navigator.WebDriverWait") as mock_wait:
            mock_wait_instance = Mock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.return_value = True

            with patch("panel_navigator.time.sleep"):
                current_panel = {
                    "name": "Test",
                    "url": "http://test.com",
                    "duration": 10,
                }

                # Should not raise exception even if JS fails
                result = self.navigator.navigate_to_panel(mock_driver, current_panel)

                # Navigation should still succeed
                assert result is True

    def test_skip_overlay_when_auth_disabled(self):
        """Test that overlay is skipped when authentication is disabled."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "complete"

        # Mock auth handler with auth_enabled = False
        mock_auth_handler = Mock()
        mock_auth_handler.auth_enabled = False
        mock_auth_handler.is_login_page.return_value = False
        mock_auth_handler.is_totp_page.return_value = False
        mock_auth_handler.check_and_handle_authentication.return_value = True

        with patch("panel_navigator.WebDriverWait") as mock_wait:
            mock_wait_instance = Mock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.return_value = True

            with patch("panel_navigator.time.sleep"):
                current_panel = {
                    "name": "Test",
                    "url": "http://test.com",
                    "duration": 10,
                }

                result = self.navigator.navigate_to_panel(
                    mock_driver, current_panel, auth_handler=mock_auth_handler
                )

                assert result is True
                # Should navigate directly without showing overlay
                mock_driver.get.assert_called_once()
                # execute_script should not be called for overlay
                mock_driver.execute_script.assert_not_called()

    def test_skip_overlay_when_on_login_page(self):
        """Test that overlay is skipped when currently on a login page."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = "complete"

        # Mock auth handler on login page
        mock_auth_handler = Mock()
        mock_auth_handler.auth_enabled = True
        mock_auth_handler.is_login_page.return_value = True  # Currently on login page
        mock_auth_handler.is_totp_page.return_value = False
        mock_auth_handler.check_and_handle_authentication.return_value = True

        with patch("panel_navigator.WebDriverWait") as mock_wait:
            mock_wait_instance = Mock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.return_value = True

            with patch("panel_navigator.time.sleep"):
                current_panel = {
                    "name": "Test",
                    "url": "http://test.com",
                    "duration": 10,
                }

                result = self.navigator.navigate_to_panel(
                    mock_driver, current_panel, auth_handler=mock_auth_handler
                )

                assert result is True
                # Should navigate directly without showing overlay
                mock_driver.get.assert_called_once()
                # execute_script should not be called for overlay
                mock_driver.execute_script.assert_not_called()
