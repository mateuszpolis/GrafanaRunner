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

            self.logger.info(f"Browser initialized: {browser_type}")

        except WebDriverException as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            raise

    def setup_chrome(self):
        """Setup Chrome browser with kiosk mode options"""
        options = ChromeOptions()

        # Kiosk mode options
        if self.config["browser_settings"].get("fullscreen", True):
            options.add_argument("--kiosk")
            options.add_argument("--start-fullscreen")

        # Security and UI options
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
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")

        # Remove bars and UI elements
        options.add_argument("--hide-scrollbars")

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

        # Additional kiosk-specific options
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--disable-blink-features=AutomationControlled")

        return webdriver.Chrome(options=options)

    def setup_firefox(self):
        """Setup Firefox browser with kiosk mode options"""
        options = FirefoxOptions()

        if self.config["browser_settings"].get("fullscreen", True):
            options.add_argument("--kiosk")

        # Additional Firefox-specific options
        (
            options.add_argument("--private-window")
            if self.config["browser_settings"].get("incognito", True)
            else None
        )

        return webdriver.Firefox(options=options)

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

        except TimeoutException:
            self.logger.warning(f"Timeout loading panel: {panel['url']}")
        except Exception as e:
            self.logger.error(f"Error loading panel {panel['url']}: {e}")

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
