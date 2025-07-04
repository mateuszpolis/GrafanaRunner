@echo off
:: Grafana Runner Startup Script
:: This script pulls the latest changes and starts the application

set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

:: Find Python executable
for /f "usebackq delims=" %%P in (`python -c "import sys; print(sys.executable)"`) do (
    set "PYTHON_EXE=%%P"
)

:: Log startup
echo [%date% %time%] Starting GrafanaRunner... >> "%CURRENT_DIR%\runner.log" 2>&1

:: Pull latest changes
echo [%date% %time%] Pulling latest changes... >> "%CURRENT_DIR%\runner.log" 2>&1
git pull >> "%CURRENT_DIR%\runner.log" 2>&1

:: Log git pull completion
echo [%date% %time%] Git pull completed, starting application... >> "%CURRENT_DIR%\runner.log" 2>&1

:: Start the application
"%PYTHON_EXE%" grafana_runner.py >> "%CURRENT_DIR%\runner.log" 2>&1
