#!/usr/bin/env python3
"""Tests for variable panel functionality."""

import json
import os
import sys
import tempfile

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ConfigManager


class TestVariablePanels:
    """Test cases for variable panel expansion."""

    def test_expand_single_variable(self):
        """Test expansion of panel with single variable."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test?var-param=param",
                    "duration": 30,
                    "variables": {"param": ["value1", "value2", "value3"]},
                }
            ],
            "browser_settings": {"browser": "chrome"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            config = manager.load_config()

            # Should have 3 expanded panels
            assert len(config["panels"]) == 3

            # Check first expanded panel
            panel = config["panels"][0]
            assert panel["name"] == "Test Panel (param=value1)"
            assert panel["url"] == "http://localhost:3000/d/test?var-param=value1"
            assert panel["duration"] == 10.0  # 30 / 3 = 10
            assert panel["original_panel"] == "Test Panel"

            # Check other panels
            assert config["panels"][1]["name"] == "Test Panel (param=value2)"
            assert (
                config["panels"][1]["url"]
                == "http://localhost:3000/d/test?var-param=value2"
            )
            assert config["panels"][2]["name"] == "Test Panel (param=value3)"
            assert (
                config["panels"][2]["url"]
                == "http://localhost:3000/d/test?var-param=value3"
            )

        finally:
            os.unlink(config_path)

    def test_expand_multiple_variables(self):
        """Test expansion of panel with multiple variables (cartesian product)."""
        config_data = {
            "panels": [
                {
                    "name": "Multi Param Panel",
                    "url": "http://localhost:3000/d/test?var-param1=param1&var-param2=param2",
                    "duration": 24,
                    "variables": {"param1": ["a", "b"], "param2": ["x", "y", "z"]},
                }
            ],
            "browser_settings": {"browser": "chrome"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            config = manager.load_config()

            # Should have 6 expanded panels (2 * 3)
            assert len(config["panels"]) == 6

            # Check first panel
            panel = config["panels"][0]
            assert panel["name"] == "Multi Param Panel (param1=a, param2=x)"
            assert (
                panel["url"] == "http://localhost:3000/d/test?var-param1=a&var-param2=x"
            )
            assert panel["duration"] == 4.0  # 24 / 6 = 4

            # Check that all combinations are present
            expected_combinations = [
                ("a", "x"),
                ("a", "y"),
                ("a", "z"),
                ("b", "x"),
                ("b", "y"),
                ("b", "z"),
            ]

            for i, (p1, p2) in enumerate(expected_combinations):
                panel = config["panels"][i]
                assert f"param1={p1}" in panel["name"]
                assert f"param2={p2}" in panel["name"]
                assert f"var-param1={p1}" in panel["url"]
                assert f"var-param2={p2}" in panel["url"]

        finally:
            os.unlink(config_path)

    def test_mixed_panels(self):
        """Test config with both regular and variable panels."""
        config_data = {
            "panels": [
                {
                    "name": "Regular Panel",
                    "url": "http://localhost:3000/d/regular",
                    "duration": 10,
                },
                {
                    "name": "Param Panel",
                    "url": "http://localhost:3000/d/param?var-type=type",
                    "duration": 20,
                    "variables": {"type": ["cpu", "memory"]},
                },
            ],
            "browser_settings": {"browser": "chrome"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            config = manager.load_config()

            # Should have 3 panels total (1 regular + 2 expanded)
            assert len(config["panels"]) == 3

            # First panel should be unchanged
            assert config["panels"][0]["name"] == "Regular Panel"
            assert config["panels"][0]["url"] == "http://localhost:3000/d/regular"
            assert config["panels"][0]["duration"] == 10
            assert "original_panel" not in config["panels"][0]

            # Other panels should be expanded
            assert config["panels"][1]["name"] == "Param Panel (type=cpu)"
            assert config["panels"][1]["duration"] == 10.0  # 20 / 2 = 10
            assert config["panels"][2]["name"] == "Param Panel (type=memory)"

        finally:
            os.unlink(config_path)

    def test_variable_validation(self):
        """Test validation of variable panels."""
        # Test invalid variables structure
        config_data = {
            "panels": [
                {
                    "name": "Invalid Panel",
                    "url": "http://localhost:3000/d/test",
                    "duration": 10,
                    "variables": "not_a_dict",  # Should be dict
                }
            ],
            "browser_settings": {"browser": "chrome"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            try:
                manager.load_config()
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "variables must be a dictionary" in str(e)

        finally:
            os.unlink(config_path)

    def test_empty_variable_values(self):
        """Test validation of empty variable values."""
        config_data = {
            "panels": [
                {
                    "name": "Empty Param Panel",
                    "url": "http://localhost:3000/d/test",
                    "duration": 10,
                    "variables": {"param": []},  # Empty list
                }
            ],
            "browser_settings": {"browser": "chrome"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            try:
                manager.load_config()
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "cannot be empty" in str(e)

        finally:
            os.unlink(config_path)

    def test_non_list_variable_values(self):
        """Test validation of non-list variable values."""
        config_data = {
            "panels": [
                {
                    "name": "Invalid Param Panel",
                    "url": "http://localhost:3000/d/test",
                    "duration": 10,
                    "variables": {"param": "not_a_list"},  # Should be list
                }
            ],
            "browser_settings": {"browser": "chrome"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            try:
                manager.load_config()
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "must be a list" in str(e)

        finally:
            os.unlink(config_path)

    def test_duration_calculation_precision(self):
        """Test that duration calculation handles rounding correctly."""
        config_data = {
            "panels": [
                {
                    "name": "Duration Test Panel",
                    "url": "http://localhost:3000/d/test?var-param=param",
                    "duration": 10,
                    "variables": {
                        "param": ["a", "b", "c"]  # 3 values, 10/3 = 3.333...
                    },
                }
            ],
            "browser_settings": {"browser": "chrome"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            config = manager.load_config()

            # All panels should have duration rounded to 1 decimal place
            for panel in config["panels"]:
                assert panel["duration"] == 3.3  # 10/3 rounded to 1 decimal

        finally:
            os.unlink(config_path)

    def test_complex_url_replacement(self):
        """Test URL parameter replacement with complex URLs."""
        config_data = {
            "panels": [
                {
                    "name": "Complex URL Panel",
                    "url": "https://example.com/d/dashboard?orgId=1&from=now-1h&to=now&var-param1=param1&refresh=30s&var-param2=param2&kiosk=true",
                    "duration": 8,
                    "variables": {"param1": ["value1"], "param2": ["value2"]},
                }
            ],
            "browser_settings": {"browser": "chrome"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            config = manager.load_config()

            panel = config["panels"][0]
            expected_url = "https://example.com/d/dashboard?orgId=1&from=now-1h&to=now&var-param1=value1&refresh=30s&var-param2=value2&kiosk=true"
            assert panel["url"] == expected_url

        finally:
            os.unlink(config_path)
