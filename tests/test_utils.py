"""Tests for utility functions and general functionality."""

import json
import os
import sys
import tempfile
from unittest.mock import Mock

# Add the parent directory to the path so we can import grafana_runner
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grafana_runner import GrafanaRunner  # noqa: E402


class TestUtilities:
    """Test cases for utility functions."""

    def test_cleanup(self):
        """Test cleanup method."""
        config_data = {
            "panels": [
                {
                    "name": "Test Panel",
                    "url": "http://localhost:3000/d/test?kiosk",
                    "duration": 10,
                }
            ],
            "browser_settings": {"browser": "chrome"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            runner = GrafanaRunner(config_path)

            # Mock a driver
            mock_driver = Mock()
            runner.driver = mock_driver

            runner.cleanup()

            # Verify driver.quit() was called
            mock_driver.quit.assert_called_once()

        finally:
            os.unlink(config_path)
