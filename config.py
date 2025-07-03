#!/usr/bin/env python3
"""Configuration handling for Grafana Runner."""

import json
import logging


class ConfigManager:
    """Handles configuration loading, validation, and creation."""

    def __init__(self, config_path="config.json"):
        """Initialize the config manager with a configuration path."""
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """Load configuration from JSON file."""
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
        """Validate the configuration structure."""
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
        """Create a default configuration file."""
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
            "grafana_kiosk_mode": True,
        }

        with open(self.config_path, "w") as f:
            json.dump(default_config, f, indent=2)

        print(f"Created default config file: {self.config_path}")
        print("Please edit the config file with your Grafana panel URLs and settings")
