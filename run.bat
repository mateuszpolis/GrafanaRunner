@echo off

:: Simple run script for Grafana Runner on Windows

echo 🚀 Starting Grafana Runner...
python grafana_runner.py %*

:: Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo ❌ Grafana Runner encountered an error.
    echo Check the logs: grafana_runner.log
    pause
)
