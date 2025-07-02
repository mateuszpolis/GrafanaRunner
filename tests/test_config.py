"""Tests for configuration loading and creation functionality."""

import json
import os
import sys
import tempfile

# Add the parent directory to the path so we can import grafana_runner
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grafana_runner import GrafanaRunner  # noqa: E402


class TestConfigurationLoading:
    """Test cases for configuration loading and creation."""

    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test?kiosk",
                    "duration": 10,
                }
            ],
            "browser_settings": {"browser": "chrome", "fullscreen": True},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)
            assert runner.config["panels"][0]["name"] == "Test Panel"
            assert runner.config["browser_settings"]["browser"] == "chrome"
        finally:
            os.unlink(config_path)

    def test_create_default_config(self):
        """Test creation of default configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")

            GrafanaRunner(config_path)

            # Should create default config
            assert os.path.exists(config_path)

            with open(config_path, "r") as f:
                config = json.load(f)

            assert "panels" in config
            assert "browser_settings" in config
            assert len(config["panels"]) > 0

    def test_default_config_includes_ssl_setting(self):
        """Test that default configuration includes ignore_ssl_errors setting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")

            GrafanaRunner(config_path)

            # Should create default config
            assert os.path.exists(config_path)

            with open(config_path, "r") as f:
                config = json.load(f)

            assert "ignore_ssl_errors" in config["browser_settings"]
            assert config["browser_settings"]["ignore_ssl_errors"] is True
