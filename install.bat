@echo off
setlocal

:: Grafana Runner Installation Script for Windows

echo Installing Grafana Runner for Windows...
echo.

:: ── Ensure running as Administrator ───────────────────────────────────────────
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: This installer must be run as Administrator.
    echo Right-click install.bat and choose "Run as administrator."
    pause
    exit /b 1
)

:: ── Check if Python is installed ──────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: ── Report Python version ─────────────────────────────────────────────────────
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

:: ── Check if pip is available ─────────────────────────────────────────────────
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available.
    echo Please reinstall Python with pip included.
    pause
    exit /b 1
)

:: ── Install Python dependencies ───────────────────────────────────────────────
echo Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

:: ── Check if Chrome is installed ──────────────────────────────────────────────
set "CHROME_PATH="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
) else (
    if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
        set "CHROME_PATH=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
    ) else (
        echo WARNING: Google Chrome not found in standard locations.
        echo Please install Chrome for best compatibility:
        echo   https://www.google.com/chrome/
        echo Or use Firefox by setting browser=firefox in config.json
        echo.
    )
)
echo ChromeDriver will be automatically managed by webdriver-manager
echo.

:: ── Get current directory for task creation ──────────────────────────────────
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

:: ── Find out where python.exe lives ────────────────────────────────
for /f "usebackq delims=" %%P in (`python -c "import sys; print(sys.executable)"`) do (
    set "PYTHON_EXE=%%P"
)
echo Using Python interpreter at: %PYTHON_EXE%

:: ── Create Windows startup task ──────────────────────────────────────────────
echo Creating Windows startup task…
schtasks /create ^
    /tn "GrafanaRunner" ^
    /tr "\"%CURRENT_DIR%\startup.bat\"" ^
    /sc onlogon ^
    /rl LIMITED ^
    /f

if errorlevel 1 (
    echo WARNING: Could not create startup task automatically.
    echo You can manually add it in Task Scheduler:
    echo   • Trigger: At log on
    echo   • Action: Start a program
    echo     Program/script: "%CURRENT_DIR%\startup.bat"
    echo   • Run with limited privileges: Yes
    echo   • Run only when user is logged on: Yes
) else (
    echo Created Windows startup task: GrafanaRunner
    echo Task will run immediately after logon with limited privileges
)

echo.
echo Installation complete!
echo.
echo Next Steps:
echo   1. Edit config.json with your Grafana panel URLs
echo   2. Test the runner: python grafana_runner.py   Or: run.bat
echo   3. Test the startup script: startup.bat
echo   4. The startup task will run immediately after your next logon
echo   5. Check runner.log for startup and error messages
echo   6. To disable: schtasks /delete /tn "GrafanaRunner" /f
echo   7. To re-enable: schtasks /change /tn "GrafanaRunner" /enable
echo.
pause
