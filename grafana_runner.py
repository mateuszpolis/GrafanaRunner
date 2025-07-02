#!/usr/bin/env python3
"""Grafana Panel Runner - A digital signage solution for Grafana dashboards.

Rotates through configured Grafana panels in full-screen browser mode.
"""

import json
import logging
import signal
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait


class GrafanaRunner:
    """Main class for managing Grafana panel rotation in kiosk mode."""

    def __init__(self, config_path="config.json"):
        """Initialize the Grafana Runner with configuration"""
        self.config_path = config_path
        self.config = self.load_config()
        self.driver = None
        self.current_panel_index = 0
        self.setup_logging()

        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get("log_level", "INFO").upper())
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("grafana_runner.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
            self.validate_config(config)
            return config
        except FileNotFoundError:
            self.create_default_config()
            return self.load_config()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def validate_config(self, config):
        """Validate the configuration structure"""
        required_keys = ["panels", "browser_settings"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")

        if not config["panels"]:
            raise ValueError("No panels configured")

        for i, panel in enumerate(config["panels"]):
            if "url" not in panel:
                raise ValueError(f"Panel {i} missing URL")
            if "duration" not in panel:
                raise ValueError(f"Panel {i} missing duration")

    def create_default_config(self):
        """Create a default configuration file"""
        default_config = {
            "panels": [
                {
                    "name": "Dashboard 1",
                    "url": "http://localhost:3000/d/dashboard1?orgId=1&refresh=5s&kiosk",
                    "duration": 10,
                },
                {
                    "name": "Dashboard 2",
                    "url": "http://localhost:3000/d/dashboard2?orgId=1&refresh=5s&kiosk",
                    "duration": 15,
                },
            ],
            "browser_settings": {
                "browser": "chrome",
                "fullscreen": True,
                "disable_extensions": True,
                "disable_web_security": False,
                "ignore_ssl_errors": True,
                "incognito": True,
                "page_load_timeout": 30,
            },
            "log_level": "INFO",
            "refresh_browser_after_cycles": 10,
        }

        with open(self.config_path, "w") as f:
            json.dump(default_config, f, indent=2)

        print(f"Created default config file: {self.config_path}")
        print("Please edit the config file with your Grafana panel URLs and settings")

    def setup_browser(self):
        """Initialize and configure the web browser"""
        browser_type = self.config["browser_settings"].get("browser", "chrome").lower()

        try:
            if browser_type == "chrome":
                self.driver = self.setup_chrome()
            elif browser_type == "firefox":
                self.driver = self.setup_firefox()
            else:
                raise ValueError(f"Unsupported browser: {browser_type}")

            # Configure timeouts
            timeout = self.config["browser_settings"].get("page_load_timeout", 30)
            self.driver.set_page_load_timeout(timeout)
            self.driver.implicitly_wait(10)

            if self.config["browser_settings"].get("fullscreen", True):
                # first, push the window into OS fullscreen
                self.driver.fullscreen_window()
                # give the OS a moment
                time.sleep(1)
                self.logger.info("Entered OS-level fullscreen")

            self.logger.info(f"Browser initialized: {browser_type}")

        except WebDriverException as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            raise

    def setup_chrome(self):
        """Setup Chrome browser with kiosk mode options"""
        options = ChromeOptions()

        # True kiosk: strip out browser chrome, then OS fullscreen
        fullscreen = self.config["browser_settings"].get("fullscreen", True)
        if fullscreen:
            # use "app" mode to remove address bar etc.
            first_panel = self.config["panels"][0]["url"]
            options.add_argument(f"--app={first_panel}")
            # add the right flag per OS
            import sys

            if sys.platform.startswith("linux"):
                options.add_argument("--kiosk")
            else:
                options.add_argument("--start-fullscreen")

        # Complete UI removal for kiosk mode
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-sync")
        options.add_argument(
            "--disable-features=TranslateUI,OptimizationHints,MediaRouter"
        )
        options.add_argument("--disable-ipc-flooding-protection")

        # Remove all UI elements and controls
        options.add_argument("--hide-scrollbars")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-password-generation")
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--disable-session-crashed-bubble")
        options.add_argument("--disable-component-extensions-with-background-pages")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-prompt-on-repost")

        # Additional kiosk mode enhancements
        options.add_argument("--noerrdialogs")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-gpu-logging")
        options.add_argument("--silent")
        options.add_argument("--log-level=3")

        # Media and autoplay settings for digital signage
        options.add_argument("--autoplay-policy=no-user-gesture-required")
        options.add_argument("--disable-features=PreloadMediaEngagementData")

        # Performance and stability options
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu-sandbox")
        options.add_argument("--disable-software-rasterizer")

        # Security options
        if self.config["browser_settings"].get("disable_web_security", False):
            options.add_argument("--disable-web-security")

        # SSL/Certificate bypass options (for internal/self-signed certificates)
        if self.config["browser_settings"].get("ignore_ssl_errors", True):
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--ignore-ssl-errors")
            options.add_argument("--ignore-certificate-errors-spki-list")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-insecure-localhost")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--test-type")

        if self.config["browser_settings"].get("disable_extensions", True):
            options.add_argument("--disable-extensions")

        if self.config["browser_settings"].get("incognito", True):
            options.add_argument("--incognito")

        # Additional kiosk-specific options to hide automation
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Set preferences to disable various popups and notifications
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,  # Block notifications
                "media_stream": 2,  # Block camera/microphone
                "geolocation": 2,  # Block location
            },
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.popups": 0,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        }
        options.add_experimental_option("prefs", prefs)

        return webdriver.Chrome(options=options)

    def setup_firefox(self):
        """Setup Firefox browser with kiosk mode options"""
        options = FirefoxOptions()

        # Kiosk mode options for Firefox
        if self.config["browser_settings"].get("fullscreen", True):
            options.add_argument("--kiosk")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")

        # Additional Firefox-specific options
        if self.config["browser_settings"].get("incognito", True):
            options.add_argument("--private-window")

        # Disable various Firefox UI elements and notifications
        options.add_argument("--no-first-run")
        options.add_argument("--disable-notifications")

        # Set Firefox preferences for kiosk mode
        options.set_preference("browser.fullscreen.autohide", True)
        options.set_preference("dom.disable_open_during_load", False)
        options.set_preference("dom.disable_window_open_feature.close", True)
        options.set_preference("dom.disable_window_open_feature.location", True)
        options.set_preference("dom.disable_window_open_feature.menubar", True)
        options.set_preference("dom.disable_window_open_feature.resizable", True)
        options.set_preference("dom.disable_window_open_feature.scrollbars", True)
        options.set_preference("dom.disable_window_open_feature.status", True)
        options.set_preference("dom.disable_window_open_feature.toolbar", True)
        options.set_preference("browser.link.open_newwindow", 1)
        options.set_preference("browser.link.open_newwindow.restriction", 0)

        # Disable notifications and popups
        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("dom.push.enabled", False)
        options.set_preference("geo.enabled", False)
        options.set_preference("media.navigator.enabled", False)

        # Performance settings
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", True)
        options.set_preference("browser.sessionstore.max_tabs_undo", 0)
        options.set_preference("browser.sessionstore.max_windows_undo", 0)

        return webdriver.Firefox(options=options)

    def ensure_fullscreen_mode(self):
        """Ensure the browser window is in fullscreen mode"""
        try:
            # Only try fullscreen if not already in app mode
            if not self.config["browser_settings"].get("fullscreen", True):
                # Maximize first
                self.driver.maximize_window()

                # Try fullscreen API
                self.driver.execute_script(
                    """
                    if (document.documentElement.requestFullscreen) {
                        document.documentElement.requestFullscreen();
                    } else if (document.documentElement.webkitRequestFullscreen) {
                        document.documentElement.webkitRequestFullscreen();
                    } else if (document.documentElement.mozRequestFullScreen) {
                        document.documentElement.mozRequestFullScreen();
                    } else if (document.documentElement.msRequestFullscreen) {
                        document.documentElement.msRequestFullscreen();
                    }
                    """
                )

                # Position window
                self.driver.set_window_position(0, 0)

                # Allow transition
                time.sleep(1)

            self.logger.info("Fullscreen mode activated")

        except Exception as e:
            self.logger.warning(f"Could not ensure fullscreen mode: {e}")
            # Continue execution even if fullscreen fails

    def navigate_to_panel(self, panel):
        """Navigate to a specific Grafana panel"""
        try:
            self.logger.info(
                f"Loading panel: {panel.get('name', 'Unnamed')} - {panel['url']}"
            )
            self.driver.get(panel["url"])

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Additional wait for Grafana panels to render
            time.sleep(3)

            # Apply kiosk mode enhancements after page load
            # self.apply_kiosk_enhancements()

        except TimeoutException:
            self.logger.warning(f"Timeout loading panel: {panel['url']}")
        except Exception as e:
            self.logger.error(f"Error loading panel {panel['url']}: {e}")

    def apply_kiosk_enhancements(self):
        """Apply additional kiosk mode enhancements via JavaScript"""
        try:
            # Hide cursor and apply kiosk-specific styling
            self.driver.execute_script(
                """
                // Hide cursor for true kiosk experience
                var style = document.createElement('style');
                style.innerHTML = `
                    * {
                        cursor: none !important;
                        -webkit-user-select: none !important;
                        -moz-user-select: none !important;
                        -ms-user-select: none !important;
                        user-select: none !important;
                    }

                    /* Hide scrollbars */
                    ::-webkit-scrollbar {
                        display: none !important;
                    }

                    /* Ensure full screen usage */
                    html, body {
                        margin: 0 !important;
                        padding: 0 !important;
                        overflow: hidden !important;
                        width: 100vw !important;
                        height: 100vh !important;
                    }

                    /* Prevent text selection highlighting */
                    ::selection {
                        background: transparent !important;
                    }
                    ::-moz-selection {
                        background: transparent !important;
                    }
                `;
                document.head.appendChild(style);

                // Disable right-click context menu
                document.addEventListener('contextmenu', function(e) {
                    e.preventDefault();
                    return false;
                });

                // Disable common keyboard shortcuts
                document.addEventListener('keydown', function(e) {
                    // Disable F11 (fullscreen toggle), F12 (dev tools), Ctrl+Shift+I, etc.
                    if (e.key === 'F11' || e.key === 'F12' ||
                        (e.ctrlKey && e.shiftKey && e.key === 'I') ||
                        (e.ctrlKey && e.shiftKey && e.key === 'J') ||
                        (e.ctrlKey && e.key === 'u') ||
                        (e.ctrlKey && e.key === 'U')) {
                        e.preventDefault();
                        return false;
                    }
                });

                // Remove any existing focus
                if (document.activeElement) {
                    document.activeElement.blur();
                }
            """
            )

        except Exception as e:
            self.logger.warning(f"Could not apply kiosk enhancements: {e}")
            # Continue execution even if enhancements fail

    def run(self):
        """Main execution loop"""
        self.logger.info("Starting Grafana Runner")

        try:
            self.setup_browser()
            cycles_completed = 0
            refresh_after_cycles = self.config.get("refresh_browser_after_cycles", 10)

            while True:
                for panel in self.config["panels"]:
                    self.navigate_to_panel(panel)

                    # Display panel for specified duration
                    duration = panel["duration"]
                    self.logger.info(f"Displaying panel for {duration} seconds")
                    time.sleep(duration)

                cycles_completed += 1
                self.logger.info(f"Completed cycle {cycles_completed}")

                # Optionally refresh browser to prevent memory leaks
                if (
                    refresh_after_cycles > 0
                    and cycles_completed % refresh_after_cycles == 0
                ):
                    self.logger.info("Refreshing browser to prevent memory issues")
                    self.refresh_browser()

        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
        finally:
            self.cleanup()

    def refresh_browser(self):
        """Refresh browser session to prevent memory leaks"""
        try:
            if self.driver:
                self.driver.quit()
            self.setup_browser()
        except Exception as e:
            self.logger.error(f"Error refreshing browser: {e}")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")


def main():
    """Main entry point"""
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"

    try:
        runner = GrafanaRunner(config_file)
        runner.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
