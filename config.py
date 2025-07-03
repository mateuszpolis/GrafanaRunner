#!/usr/bin/env python3
"""Configuration handling for Grafana Runner."""

import itertools
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

            # Expand parameterized panels
            config["panels"] = self.expand_panels(config["panels"])

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

            # Validate variables if present
            if "variables" in panel:
                if not isinstance(panel["variables"], dict):
                    raise ValueError(f"Panel {i} variables must be a dictionary")
                for var_name, var_values in panel["variables"].items():
                    if not isinstance(var_values, list):
                        raise ValueError(
                            f"Panel {i} variable '{var_name}' must be a list"
                        )
                    if not var_values:
                        raise ValueError(
                            f"Panel {i} variable '{var_name}' cannot be empty"
                        )

    def expand_panels(self, panels):
        """Expand panels with variables into individual panels with all combinations."""
        expanded_panels = []

        for panel in panels:
            if "variables" in panel:
                # Generate all variable combinations
                var_names = list(panel["variables"].keys())
                var_values = list(panel["variables"].values())
                combinations = list(itertools.product(*var_values))

                if not combinations:
                    # No combinations possible, skip this panel
                    self.logger.warning(
                        f"Panel '{panel.get('name', 'Unnamed')}' has no valid variable combinations"
                    )
                    continue

                # Calculate duration per combination
                total_duration = panel["duration"]
                duration_per_combination = round(total_duration / len(combinations), 1)

                self.logger.info(
                    f"Expanding panel '{panel.get('name', 'Unnamed')}' into {len(combinations)} combinations"
                )

                # Create a panel for each combination
                for i, combination in enumerate(combinations):
                    # Create variable mapping
                    var_map = dict(zip(var_names, combination))

                    # Replace variables in URL
                    expanded_url = panel["url"]
                    for var_name, var_value in var_map.items():
                        placeholder = f"var-{var_name}={var_name}"
                        replacement = f"var-{var_name}={var_value}"
                        expanded_url = expanded_url.replace(placeholder, replacement)

                    # Create expanded panel
                    expanded_panel = {
                        "name": f"{panel.get('name', 'Unnamed')} ({', '.join(f'{k}={v}' for k, v in var_map.items())})",
                        "url": expanded_url,
                        "duration": duration_per_combination,
                        "original_panel": panel.get("name", "Unnamed"),
                        "variables": var_map,
                    }

                    expanded_panels.append(expanded_panel)
            else:
                # Panel without variables, add as-is
                expanded_panels.append(panel)

        return expanded_panels

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
                {
                    "name": "Parameterized Dashboard",
                    "url": "http://localhost:3000/d/dashboard3?orgId=1&var-param=param&var-region=region&kiosk",
                    "duration": 30,
                    "variables": {
                        "param": ["cpu", "memory", "disk"],
                        "region": ["us-east", "us-west"],
                    },
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
