#!/usr/bin/env python3
"""Tests for the authentication handler module."""

import os
from unittest.mock import Mock, patch

from selenium.common.exceptions import NoSuchElementException

from auth_handler import AuthHandler


class TestAuthHandler:
    """Test cases for the AuthHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {}

        # Mock environment variables
        self.env_vars = {
            "CERN_USERNAME": "testuser",
            "CERN_PASSWORD": "testpass",
            "CERN_TOTP_SECRET": "JBSWY3DPEHPK3PXP",
        }

    @patch.dict(
        os.environ,
        {
            "CERN_USERNAME": "testuser",
            "CERN_PASSWORD": "testpass",
            "CERN_TOTP_SECRET": "JBSWY3DPEHPK3PXP",
        },
    )
    def test_load_credentials_success(self):
        """Test successful credential loading."""
        auth_handler = AuthHandler(self.config)

        assert auth_handler.username == "testuser"
        assert auth_handler.password == "testpass"
        assert auth_handler.totp_secret == "JBSWY3DPEHPK3PXP"
        assert auth_handler.auth_enabled is True

    def test_load_credentials_missing(self):
        """Test credential loading with missing environment variables."""
        # Clear environment variables and patch load_dotenv
        with patch.dict(os.environ, {}, clear=True), patch(
            "dotenv.load_dotenv", side_effect=ImportError("dotenv not available")
        ):
            auth_handler = AuthHandler(self.config)
            assert auth_handler.auth_enabled is False

    def test_is_login_page_detection(self):
        """Test login page detection."""
        auth_handler = AuthHandler(self.config)
        auth_handler.auth_enabled = True

        mock_driver = Mock()

        # Test various login URLs
        test_urls = [
            "https://agrana.cern.ch/login",
            "https://agrana.cern.ch/login/generic_oauth",
            "https://auth.cern.ch/auth/realms/cern",
            "https://example.com/login",
        ]

        for url in test_urls:
            mock_driver.current_url = url
            assert auth_handler.is_login_page(mock_driver) is True

        # Test non-login URL
        mock_driver.current_url = "https://agrana.cern.ch/dashboard"
        assert auth_handler.is_login_page(mock_driver) is False

    def test_is_totp_page_detection(self):
        """Test TOTP page detection."""
        auth_handler = AuthHandler(self.config)
        auth_handler.auth_enabled = True

        mock_driver = Mock()

        # Test TOTP page detection - element found
        mock_driver.find_element.return_value = Mock()
        assert auth_handler.is_totp_page(mock_driver) is True

        # Test TOTP page detection - element not found
        mock_driver.find_element.side_effect = NoSuchElementException()
        assert auth_handler.is_totp_page(mock_driver) is False

    @patch.dict(
        os.environ,
        {
            "CERN_USERNAME": "testuser",
            "CERN_PASSWORD": "testpass",
            "CERN_TOTP_SECRET": "JBSWY3DPEHPK3PXP",
        },
    )
    def test_generate_totp_code(self):
        """Test TOTP code generation."""
        auth_handler = AuthHandler(self.config)

        code = auth_handler._generate_totp_code()

        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()

    def test_check_and_handle_authentication_disabled(self):
        """Test authentication check when disabled."""
        auth_handler = AuthHandler(self.config)
        auth_handler.auth_enabled = False

        mock_driver = Mock()
        mock_driver.current_url = "https://agrana.cern.ch/dashboard"

        # Should return True when auth is disabled and not on login page
        assert auth_handler.check_and_handle_authentication(mock_driver) is True

        # Should return False when auth is disabled but on login page
        mock_driver.current_url = "https://agrana.cern.ch/login"
        assert auth_handler.check_and_handle_authentication(mock_driver) is False

    @patch.dict(
        os.environ,
        {
            "CERN_USERNAME": "testuser",
            "CERN_PASSWORD": "testpass",
            "CERN_TOTP_SECRET": "JBSWY3DPEHPK3PXP",
        },
    )
    def test_check_and_handle_authentication_enabled(self):
        """Test authentication check when enabled."""
        auth_handler = AuthHandler(self.config)

        mock_driver = Mock()
        mock_driver.current_url = "https://agrana.cern.ch/dashboard"

        # Should return True when not on login page
        assert auth_handler.check_and_handle_authentication(mock_driver) is True

    @patch.dict(
        os.environ,
        {
            "CERN_USERNAME": "testuser",
            "CERN_PASSWORD": "testpass",
            "CERN_TOTP_SECRET": "JBSWY3DPEHPK3PXP",
        },
    )
    @patch("auth_handler.WebDriverWait")
    def test_click_cern_sso_login(self, mock_wait):
        """Test clicking CERN SSO login button."""
        auth_handler = AuthHandler(self.config)

        mock_driver = Mock()
        mock_element = Mock()
        mock_wait.return_value.until.return_value = mock_element

        result = auth_handler._click_cern_sso_login(mock_driver)

        assert result is True
        mock_element.click.assert_called_once()

    @patch.dict(
        os.environ,
        {
            "CERN_USERNAME": "testuser",
            "CERN_PASSWORD": "testpass",
            "CERN_TOTP_SECRET": "JBSWY3DPEHPK3PXP",
        },
    )
    @patch("auth_handler.WebDriverWait")
    def test_fill_login_credentials(self, mock_wait):
        """Test filling login credentials."""
        auth_handler = AuthHandler(self.config)

        mock_driver = Mock()
        mock_username_field = Mock()
        mock_password_field = Mock()
        mock_form = Mock()

        # Setup mocks
        mock_wait.return_value.until.return_value = mock_username_field
        mock_driver.find_element.side_effect = [mock_password_field, mock_form]

        result = auth_handler._fill_login_credentials(mock_driver)

        assert result is True
        mock_username_field.clear.assert_called_once()
        mock_username_field.send_keys.assert_called_once_with("testuser")
        mock_password_field.clear.assert_called_once()
        mock_password_field.send_keys.assert_called_once_with("testpass")
        mock_form.submit.assert_called_once()

    @patch.dict(
        os.environ,
        {
            "CERN_USERNAME": "testuser",
            "CERN_PASSWORD": "testpass",
            "CERN_TOTP_SECRET": "JBSWY3DPEHPK3PXP",
        },
    )
    @patch("auth_handler.WebDriverWait")
    def test_handle_totp_authentication(self, mock_wait):
        """Test TOTP authentication handling."""
        auth_handler = AuthHandler(self.config)

        mock_driver = Mock()
        mock_otp_field = Mock()
        mock_form = Mock()

        # Setup mocks
        mock_wait.return_value.until.return_value = mock_otp_field
        mock_driver.find_element.return_value = mock_form

        # Mock TOTP generation
        with patch.object(auth_handler, "_generate_totp_code", return_value="123456"):
            auth_handler._handle_totp_authentication(mock_driver)

        mock_otp_field.clear.assert_called_once()
        mock_otp_field.send_keys.assert_called_once_with("123456")
        mock_form.submit.assert_called_once()

    @patch.dict(
        os.environ,
        {
            "CERN_USERNAME": "testuser",
            "CERN_PASSWORD": "testpass",
            "CERN_TOTP_SECRET": "JBSWY3DPEHPK3PXP",
        },
    )
    def test_wait_for_successful_authentication(self):
        """Test waiting for successful authentication."""
        auth_handler = AuthHandler(self.config)

        mock_driver = Mock()
        mock_driver.current_url = "https://agrana.cern.ch/dashboard"

        result = auth_handler._wait_for_successful_authentication(mock_driver)

        assert result is True
