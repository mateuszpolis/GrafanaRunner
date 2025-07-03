#!/usr/bin/env python3
"""Authentication handler for Grafana Runner with CERN SSO support."""

import logging
import os
import time

import pyotp
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class AuthHandler:
    """Handles Grafana authentication with CERN SSO and TOTP."""

    def __init__(self, config):
        """Initialize the authentication handler."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.load_credentials()

    def load_credentials(self):
        """Load authentication credentials from environment variables."""
        try:
            # Try to load from .env file if python-dotenv is available
            try:
                from dotenv import load_dotenv

                load_dotenv(".env.local")  # Try local first
                if not os.getenv("CERN_USERNAME"):
                    load_dotenv(".env")  # Fallback to .env
            except ImportError:
                self.logger.warning(
                    "python-dotenv not installed. Using system environment variables only."
                )

            self.username = os.getenv("CERN_USERNAME")
            self.password = os.getenv("CERN_PASSWORD")
            self.totp_secret = os.getenv("CERN_TOTP_SECRET")

            if not all([self.username, self.password, self.totp_secret]):
                missing = []
                if not self.username:
                    missing.append("CERN_USERNAME")
                if not self.password:
                    missing.append("CERN_PASSWORD")
                if not self.totp_secret:
                    missing.append("CERN_TOTP_SECRET")

                self.logger.warning(
                    f"Missing authentication environment variables: {', '.join(missing)}"
                )
                self.logger.warning(
                    "Authentication will be disabled. Set these variables to enable auto-login."
                )
                self.auth_enabled = False
                return

            self.logger.info("Authentication credentials loaded successfully")
            self.auth_enabled = True

        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            raise

    def is_login_page(self, driver):
        """Check if the current page is a login page."""
        current_url = driver.current_url
        login_indicators = [
            "agrana.cern.ch/login",
            "login/generic_oauth",
            "auth.cern.ch",
            "/login",
        ]

        for indicator in login_indicators:
            if indicator in current_url:
                self.logger.info(f"Login page detected: {current_url}")
                return True

        return False

    def is_totp_page(self, driver):
        """Check if the current page is the TOTP/OTP page."""
        try:
            # Look for OTP input field
            driver.find_element(By.ID, "otp")
            self.logger.info("TOTP page detected")
            return True
        except NoSuchElementException:
            return False

    def handle_authentication(self, driver):
        """Handle the complete authentication flow."""
        try:
            self.logger.info("Starting authentication flow")

            # Step 1: Click CERN SSO login if we're on the main login page
            if self._click_cern_sso_login(driver):
                # Wait for redirect to CERN auth page
                time.sleep(2)

            # Step 2: Fill in credentials if we're on the login form
            if self._fill_login_credentials(driver):
                # Wait for redirect to TOTP page
                time.sleep(2)

            # Step 3: Handle TOTP if we're on the OTP page
            if self.is_totp_page(driver):
                self._handle_totp_authentication(driver)
                # Wait for final redirect back to Grafana
                time.sleep(3)

            # Wait for redirect back to original page
            self._wait_for_successful_authentication(driver)

            self.logger.info("Authentication completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False

    def _click_cern_sso_login(self, driver):
        """Click on the CERN SSO login link."""
        try:
            # Look for the CERN SSO login button
            sso_selectors = [
                "a[href='login/generic_oauth']",
                "a.css-st1idm-button[href='login/generic_oauth']",
                "//a[contains(@href, 'login/generic_oauth')]",
            ]

            for selector in sso_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS selector
                        element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )

                    element.click()
                    self.logger.info("Clicked CERN SSO login button")
                    return True

                except TimeoutException:
                    continue

            self.logger.warning("CERN SSO login button not found")
            return False

        except Exception as e:
            self.logger.error(f"Failed to click CERN SSO login: {e}")
            return False

    def _fill_login_credentials(self, driver):
        """Fill in username and password on the login form."""
        try:
            # Wait for username field and fill it
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            self.logger.info("Username entered")

            # Fill password field
            password_field = driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            self.logger.info("Password entered")

            # Submit the form
            login_form = driver.find_element(By.ID, "kc-form-login")
            login_form.submit()
            self.logger.info("Login form submitted")

            return True

        except TimeoutException:
            self.logger.warning("Login form not found or timeout")
            return False
        except NoSuchElementException as e:
            self.logger.warning(f"Login form element not found: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to fill login credentials: {e}")
            return False

    def _generate_totp_code(self):
        """Generate TOTP code using the secret."""
        try:
            totp = pyotp.TOTP(self.totp_secret)
            code = totp.now()
            self.logger.info("TOTP code generated")
            return code
        except Exception as e:
            self.logger.error(f"Failed to generate TOTP code: {e}")
            raise

    def _handle_totp_authentication(self, driver):
        """Handle TOTP/OTP authentication."""
        try:
            # Generate TOTP code
            totp_code = self._generate_totp_code()

            # Wait for OTP input field and fill it
            otp_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "otp"))
            )
            otp_field.clear()
            otp_field.send_keys(totp_code)
            self.logger.info("TOTP code entered")

            # Submit the OTP form
            otp_form = driver.find_element(By.ID, "kc-otp-login-form")
            otp_form.submit()
            self.logger.info("TOTP form submitted")

        except TimeoutException:
            self.logger.error("TOTP form not found or timeout")
            raise
        except NoSuchElementException as e:
            self.logger.error(f"TOTP form element not found: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to handle TOTP authentication: {e}")
            raise

    def _wait_for_successful_authentication(self, driver):
        """Wait for successful authentication and redirect back to Grafana."""
        try:
            # Wait for redirect away from auth pages
            max_wait_time = 30
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                current_url = driver.current_url

                # Check if we're no longer on auth pages
                auth_indicators = ["login", "auth.cern.ch", "oauth", "/otp"]

                is_auth_page = any(
                    indicator in current_url.lower() for indicator in auth_indicators
                )

                if not is_auth_page and "agrana.cern.ch" in current_url:
                    self.logger.info(
                        "Successfully authenticated and redirected to Grafana"
                    )
                    return True

                time.sleep(1)

            self.logger.warning("Authentication redirect timeout")
            return False

        except Exception as e:
            self.logger.error(f"Error waiting for authentication: {e}")
            return False

    def check_and_handle_authentication(self, driver):
        """Check if authentication is needed and handle it."""
        if not self.auth_enabled:
            if self.is_login_page(driver):
                self.logger.warning(
                    "Login page detected but authentication is disabled (missing credentials)"
                )
                return False
            return True

        if self.is_login_page(driver):
            self.logger.info("Authentication required, starting login process")
            return self.handle_authentication(driver)
        return True  # No authentication needed
