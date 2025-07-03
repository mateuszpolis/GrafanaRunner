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

    def navigate_to_panel(self, driver, panel, auth_handler=None, previous_panel=None):
        """Navigate to a specific Grafana panel with professional transition overlay."""
        try:
            # Prepare URL with optional kiosk mode
            panel_url = self._prepare_panel_url(panel["url"])

            self.logger.info(
                f"Loading panel: {panel.get('name', 'Unnamed')} - {panel_url}"
            )

            # Check if authentication is likely needed before showing overlay
            skip_overlay = False
            if auth_handler:
                # Skip overlay if authentication is not enabled (no credentials loaded)
                if (
                    not hasattr(auth_handler, "auth_enabled")
                    or not auth_handler.auth_enabled
                ):
                    skip_overlay = True
                    self.logger.debug("Authentication not enabled, skipping overlay")
                # Also skip overlay if we're currently on a login page
                elif auth_handler.is_login_page(driver) or auth_handler.is_totp_page(
                    driver
                ):
                    skip_overlay = True
                    self.logger.debug(
                        "Currently on authentication page, skipping overlay"
                    )

            if skip_overlay:
                # Navigate directly without overlay for authentication
                self.logger.debug("Navigating without overlay for authentication")
                driver.get(panel_url)

                # Wait for page to load completely
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState")
                    == "complete"
                )

                # Handle authentication
                if auth_handler and not auth_handler.check_and_handle_authentication(
                    driver
                ):
                    self.logger.error(
                        "Authentication failed, cannot proceed with panel navigation"
                    )
                    return False
            else:
                # Show transition overlay for smooth experience
                self.logger.debug("Showing transition overlay for smooth navigation")

                # Get minimum transition duration
                min_overlay_duration = self.config.get(
                    "transition_overlay_min_duration", 2.0
                )

                # Show transition overlay on current page
                self.show_transition_overlay(driver, previous_panel, panel)

                # Keep overlay visible for minimum duration on current page
                self.logger.debug(
                    f"Showing transition overlay for {min_overlay_duration}s"
                )
                time.sleep(min_overlay_duration)

                # Navigate to new panel (this will clear the overlay)
                driver.get(panel_url)

                # Wait for page to load completely
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState")
                    == "complete"
                )

                # Check for authentication requirement (should be minimal since credentials are loaded)
                if auth_handler and not auth_handler.check_and_handle_authentication(
                    driver
                ):
                    self.logger.error(
                        "Authentication failed, cannot proceed with panel navigation"
                    )
                    return False

            # Additional wait for Grafana panels to render
            time.sleep(3)

            # Panel navigation completed
            self.logger.debug("Panel navigation completed successfully")

            # Apply kiosk mode enhancements after page load
            # self.apply_kiosk_enhancements(driver)

            return True

        except TimeoutException:
            self.logger.warning(f"Timeout loading panel: {panel_url}")
            self.hide_transition_overlay(driver)  # Hide overlay on timeout
            return False
        except Exception as e:
            self.logger.error(f"Error loading panel {panel_url}: {e}")
            self.hide_transition_overlay(driver)  # Hide overlay on error
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

    def show_transition_overlay(self, driver, previous_panel, current_panel):
        """Show professional transition overlay with panel information."""
        try:
            # Get panel information for display
            prev_name = (
                previous_panel.get("name", "Starting") if previous_panel else "Starting"
            )
            prev_vars = self._format_variables(previous_panel) if previous_panel else ""

            curr_name = current_panel.get("name", "Unknown Panel")
            curr_vars = self._format_variables(current_panel)

            self.logger.debug(f"Showing transition overlay: {prev_name} → {curr_name}")

            # Create and inject the transition overlay
            driver.execute_script(
                f"""
                // Remove any existing overlay
                const existingOverlay = document.getElementById('kiosk-transition-overlay');
                if (existingOverlay) {{
                    existingOverlay.remove();
                }}

                // Create overlay container
                const overlay = document.createElement('div');
                overlay.id = 'kiosk-transition-overlay';
                overlay.innerHTML = `
                    <div class="overlay-background">
                        <div class="transition-content">
                            <div class="panel-transition">
                                <div class="previous-panel">
                                    <div class="panel-label">CURRENT</div>
                                    <div class="panel-name">{prev_name}</div>
                                    <div class="panel-vars">{prev_vars}</div>
                                </div>
                                <div class="transition-arrow">
                                    <div class="spinner"></div>
                                    <div class="arrow">→</div>
                                </div>
                                <div class="next-panel">
                                    <div class="panel-label">LOADING</div>
                                    <div class="panel-name">{curr_name}</div>
                                    <div class="panel-vars">{curr_vars}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                // Add CSS styles
                const style = document.createElement('style');
                style.textContent = `
                    #kiosk-transition-overlay {{
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100vw;
                        height: 100vh;
                        z-index: 999999;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        pointer-events: none;
                    }}

                    .overlay-background {{
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        animation: fadeIn 0.3s ease-out;
                    }}

                    .transition-content {{
                        text-align: center;
                        color: white;
                        max-width: 80%;
                    }}

                    .panel-transition {{
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 60px;
                        flex-wrap: wrap;
                    }}

                    .previous-panel, .next-panel {{
                        min-width: 280px;
                        padding: 30px;
                        border-radius: 16px;
                        background: rgba(255, 255, 255, 0.05);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    }}

                    .previous-panel {{
                        animation: slideInLeft 0.5s ease-out;
                    }}

                    .next-panel {{
                        animation: slideInRight 0.5s ease-out;
                    }}

                    .panel-label {{
                        font-size: 14px;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        opacity: 0.7;
                        margin-bottom: 10px;
                    }}

                    .panel-name {{
                        font-size: 24px;
                        font-weight: 700;
                        margin-bottom: 8px;
                        line-height: 1.2;
                    }}

                    .panel-vars {{
                        font-size: 14px;
                        opacity: 0.8;
                        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                        color: #64ffda;
                        line-height: 1.4;
                    }}

                    .transition-arrow {{
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        gap: 15px;
                    }}

                    .spinner {{
                        width: 40px;
                        height: 40px;
                        border: 3px solid rgba(255, 255, 255, 0.2);
                        border-top: 3px solid #64ffda;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    }}

                    .arrow {{
                        font-size: 36px;
                        font-weight: 300;
                        opacity: 0.8;
                        animation: pulse 2s ease-in-out infinite;
                    }}

                    @keyframes fadeIn {{
                        from {{ opacity: 0; }}
                        to {{ opacity: 1; }}
                    }}

                    @keyframes slideInLeft {{
                        from {{
                            opacity: 0;
                            transform: translateX(-50px);
                        }}
                        to {{
                            opacity: 1;
                            transform: translateX(0);
                        }}
                    }}

                    @keyframes slideInRight {{
                        from {{
                            opacity: 0;
                            transform: translateX(50px);
                        }}
                        to {{
                            opacity: 1;
                            transform: translateX(0);
                        }}
                    }}

                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}

                    @keyframes pulse {{
                        0%, 100% {{ opacity: 0.8; transform: scale(1); }}
                        50% {{ opacity: 1; transform: scale(1.1); }}
                    }}

                    @media (max-width: 768px) {{
                        .panel-transition {{
                            flex-direction: column;
                            gap: 30px;
                        }}
                        .previous-panel, .next-panel {{
                            min-width: 250px;
                        }}
                        .arrow {{
                            transform: rotate(90deg);
                        }}
                    }}
                `;

                // Append to document
                document.head.appendChild(style);
                document.body.appendChild(overlay);
            """
            )

        except Exception as e:
            self.logger.warning(f"Could not show transition overlay: {e}")

    def hide_transition_overlay(self, driver):
        """Hide the transition overlay with fade-out animation."""
        try:
            driver.execute_script(
                """
                const overlay = document.getElementById('kiosk-transition-overlay');
                if (overlay) {
                    overlay.style.animation = 'fadeOut 0.3s ease-out forwards';
                    setTimeout(() => {
                        overlay.remove();
                    }, 300);
                }

                // Add fadeOut animation if not already defined
                if (!document.querySelector('style[data-fadeout]')) {
                    const style = document.createElement('style');
                    style.setAttribute('data-fadeout', 'true');
                    style.textContent = `
                        @keyframes fadeOut {
                            from { opacity: 1; }
                            to { opacity: 0; }
                        }
                    `;
                    document.head.appendChild(style);
                }
            """
            )

        except Exception as e:
            self.logger.warning(f"Could not hide transition overlay: {e}")

    def _format_variables(self, panel):
        """Format panel variables for display in the overlay."""
        if not panel or "variables" not in panel:
            return ""

        variables = panel.get("variables", {})
        if isinstance(variables, dict):
            # For expanded panels, show the actual variable values
            var_strings = []
            for key, value in variables.items():
                if isinstance(value, str):
                    var_strings.append(f"{key}={value}")
                elif isinstance(value, list) and len(value) <= 3:
                    var_strings.append(f"{key}=[{', '.join(map(str, value))}]")
                elif isinstance(value, list):
                    var_strings.append(f"{key}=[{len(value)} values]")
            return "<br>".join(var_strings)

        return ""

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
