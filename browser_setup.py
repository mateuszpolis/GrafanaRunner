#!/usr/bin/env python3
"""Browser setup and configuration for Grafana Runner."""

import logging
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class BrowserSetup:
    """Handles browser initialization and configuration."""

    def __init__(self, config):
        """Initialize the browser setup with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)

    def setup_browser(self):
        """Initialize and configure the web browser."""
        browser_type = self.config["browser_settings"].get("browser", "chrome").lower()

        try:
            if browser_type == "chrome":
                driver = self.setup_chrome()
            elif browser_type == "firefox":
                driver = self.setup_firefox()
            else:
                raise ValueError(f"Unsupported browser: {browser_type}")

            # Configure timeouts
            timeout = self.config["browser_settings"].get("page_load_timeout", 30)
            driver.set_page_load_timeout(timeout)
            driver.implicitly_wait(10)

            if self.config["browser_settings"].get("fullscreen", True):
                # first, push the window into OS fullscreen
                driver.fullscreen_window()
                # give the OS a moment
                time.sleep(1)
                self.logger.info("Entered OS-level fullscreen")

            self.logger.info(f"Browser initialized: {browser_type}")
            return driver

        except WebDriverException as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            raise

    def setup_chrome(self):
        """Setup Chrome browser with kiosk mode options."""
        options = ChromeOptions()

        # True kiosk: strip out browser chrome, then OS fullscreen
        fullscreen = self.config["browser_settings"].get("fullscreen", True)
        if fullscreen:
            # use "app" mode to remove address bar etc.
            first_panel = self.config["panels"][0]["url"]
            options.add_argument(f"--app={first_panel}")
            # add the right flag per OS
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
        """Setup Firefox browser with kiosk mode options."""
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

    def ensure_fullscreen_mode(self, driver):
        """Ensure the browser window is in fullscreen mode."""
        try:
            # Only try fullscreen if not already in app mode
            if not self.config["browser_settings"].get("fullscreen", True):
                # Maximize first
                driver.maximize_window()

                # Try fullscreen API
                driver.execute_script(
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
                driver.set_window_position(0, 0)

                # Allow transition
                time.sleep(1)

            self.logger.info("Fullscreen mode activated")

        except Exception as e:
            self.logger.warning(f"Could not ensure fullscreen mode: {e}")
            # Continue execution even if fullscreen fails
