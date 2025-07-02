"""Tests for enhanced fullscreen mode and kiosk functionality.

This test module covers the enhanced fullscreen and kiosk mode features added to GrafanaRunner:

1. Enhanced Chrome Browser Setup:
   - Tests all new Chrome flags for fullscreen mode
   - Tests Chrome preferences for kiosk mode (notifications, popups, etc.)
   - Verifies performance and stability options

2. Enhanced Firefox Browser Setup:
   - Tests Firefox fullscreen arguments and preferences
   - Verifies Firefox-specific kiosk mode settings

3. Fullscreen Mode Enforcement:
   - Tests the ensure_fullscreen_mode() method
   - Tests JavaScript fullscreen API calls
   - Tests window positioning and maximization

4. Kiosk Mode Enhancements:
   - Tests the apply_kiosk_enhancements() method
   - Tests CSS injection for cursor hiding and UI removal
   - Tests JavaScript event handling for keyboard shortcuts and right-click blocking

5. Integration Testing:
   - Tests the complete fullscreen setup flow
   - Tests navigation with kiosk enhancements
   - Tests exception handling for robustness

6. Configuration Testing:
   - Tests behavior when fullscreen is enabled vs disabled
   - Tests that enhancements are properly skipped when not needed

These tests ensure that the application provides a true kiosk experience with:
- No visible browser controls or UI elements
- Hidden cursor for digital signage
- Blocked user interactions (right-click, keyboard shortcuts)
- Proper fullscreen behavior across platforms (especially Windows)
- Robust error handling
"""

import json
import os
import sys
import tempfile
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import grafana_runner
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grafana_runner import GrafanaRunner  # noqa: E402


class TestFullscreenMode:
    """Test cases for enhanced fullscreen mode and kiosk functionality."""

    @patch("grafana_runner.webdriver.Chrome")
    def test_enhanced_chrome_fullscreen_flags(self, mock_chrome):
        """Test that all enhanced fullscreen Chrome flags are properly set."""
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

            with patch("grafana_runner.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_options.arguments = []

                def add_argument_side_effect(arg):
                    mock_options.arguments.append(arg)

                mock_options.add_argument.side_effect = add_argument_side_effect

                runner.setup_browser()

                # Verify enhanced fullscreen arguments are present
                expected_fullscreen_args = [
                    "--kiosk",
                    "--start-fullscreen",
                    "--start-maximized",
                    "--force-device-scale-factor=1",
                    "--disable-features=CalculateNativeWinOcclusion",
                    "--disable-infobars",
                    "--disable-notifications",
                    "--disable-password-generation",
                    "--disable-save-password-bubble",
                    "--disable-session-crashed-bubble",
                    "--noerrdialogs",
                    "--disable-hang-monitor",
                    "--autoplay-policy=no-user-gesture-required",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-gpu-sandbox",
                ]

                for expected_arg in expected_fullscreen_args:
                    assert (
                        expected_arg in mock_options.arguments
                    ), f"Expected enhanced fullscreen argument {expected_arg} not found in Chrome options"

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Chrome")
    def test_chrome_preferences_for_kiosk_mode(self, mock_chrome):
        """Test that Chrome preferences are properly set for kiosk mode."""
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
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            mock_driver = Mock()
            mock_chrome.return_value = mock_driver

            with patch("grafana_runner.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options

                runner.setup_browser()

                # Verify experimental options were set with preferences
                mock_options.add_experimental_option.assert_any_call(
                    "excludeSwitches", ["enable-automation", "enable-logging"]
                )

                # Check that preferences were set (should be called with "prefs" key)
                prefs_calls = [
                    call_args
                    for call_args in mock_options.add_experimental_option.call_args_list
                    if call_args[0][0] == "prefs"
                ]
                assert (
                    len(prefs_calls) > 0
                ), "Chrome preferences should be set for kiosk mode"

                # Verify the preferences structure
                prefs_call = prefs_calls[0]
                prefs_dict = prefs_call[0][1]
                assert "profile.default_content_setting_values" in prefs_dict
                assert (
                    prefs_dict["profile.default_content_setting_values"][
                        "notifications"
                    ]
                    == 2
                )

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Firefox")
    def test_enhanced_firefox_fullscreen_setup(self, mock_firefox):
        """Test enhanced Firefox fullscreen setup with preferences."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test?kiosk",
                    "duration": 10,
                }
            ],
            "browser_settings": {
                "browser": "firefox",
                "fullscreen": True,
                "incognito": True,
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            mock_driver = Mock()
            mock_firefox.return_value = mock_driver

            with patch("grafana_runner.FirefoxOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options

                runner.setup_browser()

                # Verify Firefox kiosk arguments
                mock_options.add_argument.assert_any_call("--kiosk")
                mock_options.add_argument.assert_any_call("--width=1920")
                mock_options.add_argument.assert_any_call("--height=1080")
                mock_options.add_argument.assert_any_call("--private-window")

                # Verify Firefox preferences were set
                preference_calls = mock_options.set_preference.call_args_list
                preference_dict = {call[0][0]: call[0][1] for call in preference_calls}

                expected_preferences = {
                    "browser.fullscreen.autohide": True,
                    "dom.webnotifications.enabled": False,
                    "dom.push.enabled": False,
                    "geo.enabled": False,
                    "media.navigator.enabled": False,
                    "browser.cache.disk.enable": False,
                    "browser.cache.memory.enable": True,
                }

                for pref_name, expected_value in expected_preferences.items():
                    assert (
                        pref_name in preference_dict
                    ), f"Firefox preference {pref_name} not set"
                    assert (
                        preference_dict[pref_name] == expected_value
                    ), f"Firefox preference {pref_name} has wrong value"

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Chrome")
    def test_ensure_fullscreen_mode_method(self, mock_chrome):
        """Test the ensure_fullscreen_mode method with JavaScript execution."""
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
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            runner.driver = mock_driver

            # Test the ensure_fullscreen_mode method directly
            runner.ensure_fullscreen_mode()

            # Verify driver methods were called
            mock_driver.maximize_window.assert_called_once()
            mock_driver.set_window_position.assert_called_once_with(0, 0)

            # Verify JavaScript was executed for fullscreen
            mock_driver.execute_script.assert_called_once()
            js_call = mock_driver.execute_script.call_args[0][0]

            # Check that the JavaScript contains fullscreen API calls
            assert "requestFullscreen" in js_call
            assert "webkitRequestFullscreen" in js_call
            assert "mozRequestFullScreen" in js_call
            assert "msRequestFullscreen" in js_call

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Chrome")
    def test_ensure_fullscreen_mode_exception_handling(self, mock_chrome):
        """Test that ensure_fullscreen_mode handles exceptions gracefully."""
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
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            runner.driver = mock_driver

            # Make maximize_window raise an exception
            mock_driver.maximize_window.side_effect = Exception("Browser error")

            # Method should not raise exception
            runner.ensure_fullscreen_mode()

            # Verify it tried to call maximize_window
            mock_driver.maximize_window.assert_called_once()

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Chrome")
    def test_apply_kiosk_enhancements_method(self, mock_chrome):
        """Test the apply_kiosk_enhancements method with CSS and event handling."""
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
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            runner.driver = mock_driver

            # Test the apply_kiosk_enhancements method directly
            runner.apply_kiosk_enhancements()

            # Verify JavaScript was executed
            mock_driver.execute_script.assert_called_once()
            js_call = mock_driver.execute_script.call_args[0][0]

            # Check that the JavaScript contains kiosk enhancements
            assert "cursor: none" in js_call
            assert "user-select: none" in js_call
            assert "contextmenu" in js_call
            assert "preventDefault" in js_call
            assert "keydown" in js_call
            assert "F11" in js_call
            assert "F12" in js_call

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Chrome")
    def test_apply_kiosk_enhancements_exception_handling(self, mock_chrome):
        """Test that apply_kiosk_enhancements handles exceptions gracefully."""
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
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            runner.driver = mock_driver

            # Make execute_script raise an exception
            mock_driver.execute_script.side_effect = Exception("JavaScript error")

            # Method should not raise exception
            runner.apply_kiosk_enhancements()

            # Verify it tried to execute script
            mock_driver.execute_script.assert_called_once()

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Chrome")
    @patch("grafana_runner.WebDriverWait")
    @patch("grafana_runner.time.sleep")
    def test_navigate_to_panel_with_kiosk_enhancements(
        self, mock_sleep, mock_wait, mock_chrome
    ):
        """Test that navigate_to_panel applies kiosk enhancements after loading."""
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
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            runner.driver = mock_driver

            # Mock WebDriverWait to return immediately
            mock_wait_instance = Mock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.return_value = True

            # Navigate to panel
            panel = config_data["panels"][0]
            runner.navigate_to_panel(panel)

            # Verify driver methods were called
            mock_driver.get.assert_called_once_with(panel["url"])

            # Verify WebDriverWait was used
            mock_wait.assert_called_once_with(mock_driver, 10)

            # Verify kiosk enhancements were applied (execute_script should be called)
            # The apply_kiosk_enhancements method calls execute_script
            assert mock_driver.execute_script.call_count >= 1

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Chrome")
    def test_fullscreen_mode_integration_flow(self, mock_chrome):
        """Test the complete fullscreen mode integration flow."""
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

            # Test the complete browser setup flow
            runner.setup_browser()

            # Verify driver configuration
            mock_driver.set_page_load_timeout.assert_called_with(30)
            mock_driver.implicitly_wait.assert_called_with(10)

            # Verify fullscreen mode was ensured (maximize_window should be called)
            mock_driver.maximize_window.assert_called_once()
            mock_driver.set_window_position.assert_called_once_with(0, 0)

        finally:
            os.unlink(config_path)

    @patch("grafana_runner.webdriver.Chrome")
    def test_fullscreen_disabled_skips_enhancements(self, mock_chrome):
        """Test that fullscreen enhancements are skipped when fullscreen is disabled."""
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
                "fullscreen": False,
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

            # Test browser setup with fullscreen disabled
            runner.setup_browser()

            # Verify fullscreen enhancements were NOT called
            mock_driver.maximize_window.assert_not_called()
            mock_driver.set_window_position.assert_not_called()

        finally:
            os.unlink(config_path)
