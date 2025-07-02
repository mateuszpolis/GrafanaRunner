@echo off
setlocal EnableDelayedExpansion

:: Grafana Runner Installation Script for Windows

echo 🚀 Installing Grafana Runner for Windows...
echo.

:: ── Ensure running as Administrator ────────────────────────────────────────────
net session >nul 2>&1
if errorlevel 1 (
    echo ❌ This installer must be run as Administrator.
    echo Right-click install.bat and choose "Run as administrator."
    pause
    exit /b 1
)

:: ── Check if Python is installed ───────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH.
    echo Please install Python 3.7+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: ── Check Python version ───────────────────────────────────────────────────────
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%

:: ── Check if pip is available ─────────────────────────────────────────────────
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not available.
    echo Please reinstall Python with pip included.
    pause
    exit /b 1
)

:: ── Install Python dependencies ────────────────────────────────────────────────
echo 📦 Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies.
    pause
    exit /b 1
)

:: ── Check if Chrome is installed ───────────────────────────────────────────────
set CHROME_PATH=
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
) else (
    echo ⚠️  Google Chrome not found in standard locations.
    echo Please install Chrome for best compatibility: https://www.google.com/chrome/
    echo Alternative: You can use Firefox by changing 'browser' to 'firefox' in config.json
    echo.
)

:: ChromeDriver will be managed automatically
echo 🔧 ChromeDriver will be automatically managed by webdriver-manager

:: ── Get current directory for task creation ───────────────────────────────────
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

:: ── Create Windows startup task ───────────────────────────────────────────────
echo 🔧 Creating Windows startup task...

:: Use schtasks directly (no XML) to avoid encoding issues
schtasks /create ^
    /tn "GrafanaRunner" ^
    /tr "\"%PYTHON_EXE:python=python%\" \"%CURRENT_DIR%\grafana_runner.py\"" ^
    /sc onlogon ^
    /rl leastprivileged ^
    /f
if errorlevel 1 (
    echo ⚠️  Could not create startup task automatically.
    echo You can manually add the task using Task Scheduler:
    echo    Action: Start a program
    echo    Program/script: python
    echo    Arguments: "%CURRENT_DIR%\grafana_runner.py"
    echo    Trigger: At log on
) else (
    echo ✅ Created Windows startup task: GrafanaRunner
)

echo.
echo ✅ Installation complete!
echo.
echo 📋 Next Steps:
echo  1. Edit config.json with your Grafana panel URLs
echo  2. Test the runner: python grafana_runner.py    Or: run.bat
echo  3. The startup task will run on your next logon
echo  4. To disable startup: schtasks /delete /tn "GrafanaRunner" /f
echo  5. To re-enable:      schtasks /change /tn "GrafanaRunner" /enable
echo.
echo 📖 For more information, see README.md
echo.
pause
