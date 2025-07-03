#!/usr/bin/env python3
"""Panel navigation and kiosk enhancements for Grafana Runner."""

import logging
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


class PanelNavigator:
    """Handles panel navigation and kiosk mode enhancements."""

    def __init__(self, config):
        """Initialize the panel navigator with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)

    def navigate_to_panel(self, driver, panel, auth_handler=None):
        """Navigate to a specific Grafana panel."""
        try:
            # Prepare URL with optional kiosk mode
            panel_url = self._prepare_panel_url(panel["url"])

            self.logger.info(
                f"Loading panel: {panel.get('name', 'Unnamed')} - {panel_url}"
            )
            driver.get(panel_url)

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Check for authentication requirement
            if auth_handler and not auth_handler.check_and_handle_authentication(
                driver
            ):
                self.logger.error(
                    "Authentication failed, cannot proceed with panel navigation"
                )
                return False

            # Additional wait for Grafana panels to render
            time.sleep(3)

            # Apply kiosk mode enhancements after page load
            # self.apply_kiosk_enhancements(driver)

            return True

        except TimeoutException:
            self.logger.warning(f"Timeout loading panel: {panel_url}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading panel {panel_url}: {e}")
            return False

    def _prepare_panel_url(self, url):
        """Prepare panel URL with optional Grafana kiosk mode parameter."""
        # Check if Grafana kiosk mode is enabled in config
        if self.config.get(
            "grafana_kiosk_mode", True
        ):  # Default to True for backward compatibility
            # Check if kiosk parameter is already present
            if "&kiosk" not in url and "?kiosk" not in url:
                # Handle URL fragments properly
                if "#" in url:
                    base_url, fragment = url.split("#", 1)
                    separator = "&" if "?" in base_url else "?"
                    url = f"{base_url}{separator}kiosk#{fragment}"
                else:
                    separator = "&" if "?" in url else "?"
                    url = f"{url}{separator}kiosk"
                self.logger.debug(f"Added kiosk parameter to URL: {url}")

        return url

    def apply_kiosk_enhancements(self, driver):
        """Apply additional kiosk mode enhancements via JavaScript."""
        try:
            # Hide cursor and apply kiosk-specific styling
            driver.execute_script(
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
