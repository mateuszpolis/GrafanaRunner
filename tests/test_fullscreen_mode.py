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

    @patch("browser_setup.webdriver.Chrome")
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

            with patch("browser_setup.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options
                mock_options.arguments = []

                def add_argument_side_effect(arg):
                    mock_options.arguments.append(arg)

                mock_options.add_argument.side_effect = add_argument_side_effect

                runner.driver = runner.browser_setup.setup_browser()

                # Verify new simplified fullscreen arguments are present
                # The new implementation uses --app mode with first panel URL
                assert any(
                    arg.startswith("--app=") for arg in mock_options.arguments
                ), "Expected --app flag for app mode"

                # Should have either --kiosk (Linux) or --start-fullscreen (other platforms)
                has_fullscreen_flag = any(
                    arg in ["--kiosk", "--start-fullscreen"]
                    for arg in mock_options.arguments
                )
                assert (
                    has_fullscreen_flag
                ), "Expected either --kiosk or --start-fullscreen flag"

                # Check that the app URL contains the first panel URL
                app_args = [
                    arg for arg in mock_options.arguments if arg.startswith("--app=")
                ]
                assert len(app_args) == 1, "Expected exactly one --app argument"
                assert (
                    "http://localhost:3000/d/test?kiosk" in app_args[0]
                ), "App URL should contain the first panel URL"

        finally:
            os.unlink(config_path)

    @patch("browser_setup.webdriver.Chrome")
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

            with patch("browser_setup.ChromeOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options

                runner.driver = runner.browser_setup.setup_browser()

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

    @patch("browser_setup.webdriver.Firefox")
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

            with patch("browser_setup.FirefoxOptions") as mock_options_class:
                mock_options = Mock()
                mock_options_class.return_value = mock_options

                runner.driver = runner.browser_setup.setup_browser()

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

    @patch("browser_setup.webdriver.Chrome")
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
            runner.browser_setup.ensure_fullscreen_mode(runner.driver)

            # In the new implementation, ensure_fullscreen_mode only acts when fullscreen is disabled
            # Since fullscreen is enabled in config, it should not call maximize_window
            mock_driver.maximize_window.assert_not_called()

            # Should not execute any JavaScript or set window position when in app mode
            mock_driver.execute_script.assert_not_called()
            mock_driver.set_window_position.assert_not_called()

        finally:
            os.unlink(config_path)

    @patch("browser_setup.webdriver.Chrome")
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
                "fullscreen": False,  # Disabled to test exception handling path
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
            runner.browser_setup.ensure_fullscreen_mode(runner.driver)

            # Verify it tried to call maximize_window
            mock_driver.maximize_window.assert_called_once()

        finally:
            os.unlink(config_path)

    @patch("browser_setup.webdriver.Chrome")
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
            runner.panel_navigator.apply_kiosk_enhancements(runner.driver)

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

    @patch("browser_setup.webdriver.Chrome")
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
            runner.panel_navigator.apply_kiosk_enhancements(runner.driver)

            # Verify it tried to execute script
            mock_driver.execute_script.assert_called_once()

        finally:
            os.unlink(config_path)

    @patch("browser_setup.webdriver.Chrome")
    @patch("panel_navigator.WebDriverWait")
    @patch("panel_navigator.time.sleep")
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

            # Mock WebDriverWait to return immediately for page load
            mock_wait_instance = Mock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.return_value = True  # Page load complete

            # Navigate to panel
            panel = config_data["panels"][0]
            runner.panel_navigator.navigate_to_panel(
                runner.driver, panel, previous_panel=None
            )

            # Verify driver methods were called
            mock_driver.get.assert_called_once_with(panel["url"])

            # Verify WebDriverWait was used once for page load
            mock_wait.assert_called_once_with(mock_driver, 10)

            # With transition overlay feature, execute_script is called to show overlay
            # Should be called at least once to show overlay
            assert mock_driver.execute_script.call_count >= 1

        finally:
            os.unlink(config_path)

    @patch("browser_setup.webdriver.Chrome")
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
            runner.driver = runner.browser_setup.setup_browser()

            # Verify driver configuration
            mock_driver.set_page_load_timeout.assert_called_with(30)
            mock_driver.implicitly_wait.assert_called_with(10)

            # Verify fullscreen mode was activated using OS-level fullscreen
            mock_driver.fullscreen_window.assert_called_once()

        finally:
            os.unlink(config_path)

    @patch("browser_setup.webdriver.Chrome")
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
            runner.driver = runner.browser_setup.setup_browser()

            # Verify fullscreen mode was NOT activated
            mock_driver.fullscreen_window.assert_not_called()

        finally:
            os.unlink(config_path)

    def test_grafana_kiosk_mode_url_preparation(self):
        """Test URL preparation with Grafana kiosk mode enabled."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test",
                    "duration": 10,
                }
            ],
            "browser_settings": {
                "browser": "chrome",
                "fullscreen": True,
            },
            "grafana_kiosk_mode": True,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            # Test URL without any parameters
            url = "http://localhost:3000/d/test"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert prepared_url == "http://localhost:3000/d/test?kiosk"

            # Test URL with existing parameters
            url = "http://localhost:3000/d/test?orgId=1"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert prepared_url == "http://localhost:3000/d/test?orgId=1&kiosk"

            # Test URL that already has kiosk parameter
            url = "http://localhost:3000/d/test?kiosk"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert prepared_url == "http://localhost:3000/d/test?kiosk"

        finally:
            os.unlink(config_path)

    def test_grafana_kiosk_mode_disabled(self):
        """Test URL preparation when Grafana kiosk mode is disabled."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test",
                    "duration": 10,
                }
            ],
            "browser_settings": {
                "browser": "chrome",
                "fullscreen": True,
            },
            "grafana_kiosk_mode": False,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            # Test URL preparation when kiosk mode is disabled
            url = "http://localhost:3000/d/test"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert (
                prepared_url == "http://localhost:3000/d/test"
            )  # Should remain unchanged

            # Test URL with existing parameters
            url = "http://localhost:3000/d/test?orgId=1"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert (
                prepared_url == "http://localhost:3000/d/test?orgId=1"
            )  # Should remain unchanged

        finally:
            os.unlink(config_path)

    def test_grafana_kiosk_mode_default_behavior(self):
        """Test default behavior when grafana_kiosk_mode is not specified."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test",
                    "duration": 10,
                }
            ],
            "browser_settings": {
                "browser": "chrome",
                "fullscreen": True,
            },
            # grafana_kiosk_mode not specified, should default to True
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            # Test URL preparation with default behavior (should add kiosk)
            url = "http://localhost:3000/d/test"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert prepared_url == "http://localhost:3000/d/test?kiosk"

        finally:
            os.unlink(config_path)

    def test_grafana_kiosk_mode_complex_urls(self):
        """Test URL preparation with complex URLs containing various parameters."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test",
                    "duration": 10,
                }
            ],
            "browser_settings": {
                "browser": "chrome",
                "fullscreen": True,
            },
            "grafana_kiosk_mode": True,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            # Test URL with multiple parameters
            url = "http://localhost:3000/d/test?orgId=1&refresh=5s"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert (
                prepared_url == "http://localhost:3000/d/test?orgId=1&refresh=5s&kiosk"
            )

            # Test URL that already has &kiosk
            url = "http://localhost:3000/d/test?orgId=1&kiosk&refresh=5s"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert (
                prepared_url == "http://localhost:3000/d/test?orgId=1&kiosk&refresh=5s"
            )

            # Test URL with ?kiosk at the beginning
            url = "http://localhost:3000/d/test?kiosk&orgId=1"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert prepared_url == "http://localhost:3000/d/test?kiosk&orgId=1"

        finally:
            os.unlink(config_path)

    @patch("browser_setup.webdriver.Chrome")
    @patch("panel_navigator.WebDriverWait")
    def test_navigate_to_panel_with_grafana_kiosk_integration(
        self, mock_wait, mock_chrome
    ):
        """Test panel navigation with Grafana kiosk mode URL preparation."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test",
                    "duration": 10,
                }
            ],
            "browser_settings": {
                "browser": "chrome",
                "fullscreen": True,
            },
            "grafana_kiosk_mode": True,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            mock_driver.execute_script.return_value = "complete"

            # Mock page load wait
            mock_wait_instance = Mock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.return_value = True

            panel = config_data["panels"][0]

            result = runner.panel_navigator.navigate_to_panel(
                mock_driver, panel, previous_panel=None
            )

            assert result is True
            # Verify that the URL was modified to include kiosk parameter
            mock_driver.get.assert_called_once_with(
                "http://localhost:3000/d/test?kiosk"
            )

        finally:
            os.unlink(config_path)

    def test_grafana_kiosk_mode_edge_cases(self):
        """Test edge cases for Grafana kiosk mode URL preparation."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test",
                    "duration": 10,
                }
            ],
            "browser_settings": {
                "browser": "chrome",
                "fullscreen": True,
            },
            "grafana_kiosk_mode": True,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            # Test URL with fragment
            url = "http://localhost:3000/d/test#section"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert prepared_url == "http://localhost:3000/d/test?kiosk#section"

            # Test URL with kiosk in middle of parameters
            url = "http://localhost:3000/d/test?orgId=1&kiosk=1&refresh=5s"
            prepared_url = runner.panel_navigator._prepare_panel_url(url)
            assert (
                prepared_url
                == "http://localhost:3000/d/test?orgId=1&kiosk=1&refresh=5s"
            )

        finally:
            os.unlink(config_path)
