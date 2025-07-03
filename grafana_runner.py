#!/usr/bin/env python3
"""Grafana Panel Runner - A digital signage solution for Grafana dashboards.

Rotates through configured Grafana panels in full-screen browser mode.
"""

import logging
import signal
import sys
import time

from browser_setup import BrowserSetup
from config import ConfigManager
from panel_navigator import PanelNavigator


class GrafanaRunner:
    """Main class for managing Grafana panel rotation in kiosk mode."""

    def __init__(self, config_path="config.json"):
        """Initialize the Grafana Runner with configuration"""
        self.config_path = config_path

        # Initialize configuration manager
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()

        # Initialize modules
        self.browser_setup = BrowserSetup(self.config)
        self.panel_navigator = PanelNavigator(self.config)

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

    def run(self):
        """Main execution loop"""
        self.logger.info("Starting Grafana Runner")

        try:
            self.driver = self.browser_setup.setup_browser()
            cycles_completed = 0
            refresh_after_cycles = self.config.get("refresh_browser_after_cycles", 10)

            while True:
                for panel in self.config["panels"]:
                    self.panel_navigator.navigate_to_panel(self.driver, panel)

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
            self.driver = self.browser_setup.setup_browser()
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
