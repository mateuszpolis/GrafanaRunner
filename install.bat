@echo off
setlocal EnableDelayedExpansion

:: Grafana Runner Installation Script for Windows

echo 🚀 Installing Grafana Runner for Windows...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH.
    echo Please install Python 3.7+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%

:: Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not available.
    echo Please reinstall Python with pip included.
    pause
    exit /b 1
)

:: Install Python dependencies
echo 📦 Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies.
    pause
    exit /b 1
)

:: Check if Chrome is installed
set CHROME_PATH=""
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else (
    echo ⚠️  Google Chrome not found in standard locations.
    echo Please install Chrome for best compatibility: https://www.google.com/chrome/
    echo Alternative: You can use Firefox by changing 'browser' to 'firefox' in config.json
    echo.
)

:: ChromeDriver will be managed automatically
echo 🔧 ChromeDriver will be automatically managed by webdriver-manager

:: Get current directory for task creation
set CURRENT_DIR=%~dp0
set CURRENT_DIR=%CURRENT_DIR:~0,-1%

:: Create Windows startup task
echo 🔧 Creating Windows startup task...

:: Create XML file for task scheduler
set TASK_XML=%TEMP%\grafana_runner_task.xml

echo ^<?xml version="1.0" encoding="UTF-16"?^> > "%TASK_XML%"
echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^> >> "%TASK_XML%"
echo   ^<RegistrationInfo^> >> "%TASK_XML%"
echo     ^<Description^>Grafana Runner - Digital Signage for Grafana Dashboards^</Description^> >> "%TASK_XML%"
echo   ^</RegistrationInfo^> >> "%TASK_XML%"
echo   ^<Triggers^> >> "%TASK_XML%"
echo     ^<LogonTrigger^> >> "%TASK_XML%"
echo       ^<Enabled^>true^</Enabled^> >> "%TASK_XML%"
echo     ^</LogonTrigger^> >> "%TASK_XML%"
echo   ^</Triggers^> >> "%TASK_XML%"
echo   ^<Principals^> >> "%TASK_XML%"
echo     ^<Principal id="Author"^> >> "%TASK_XML%"
echo       ^<LogonType^>InteractiveToken^</LogonType^> >> "%TASK_XML%"
echo       ^<RunLevel^>LeastPrivilege^</RunLevel^> >> "%TASK_XML%"
echo     ^</Principal^> >> "%TASK_XML%"
echo   ^</Principals^> >> "%TASK_XML%"
echo   ^<Settings^> >> "%TASK_XML%"
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^> >> "%TASK_XML%"
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^> >> "%TASK_XML%"
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^> >> "%TASK_XML%"
echo     ^<AllowHardTerminate^>true^</AllowHardTerminate^> >> "%TASK_XML%"
echo     ^<StartWhenAvailable^>false^</StartWhenAvailable^> >> "%TASK_XML%"
echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^> >> "%TASK_XML%"
echo     ^<IdleSettings^> >> "%TASK_XML%"
echo       ^<StopOnIdleEnd^>false^</StopOnIdleEnd^> >> "%TASK_XML%"
echo       ^<RestartOnIdle^>false^</RestartOnIdle^> >> "%TASK_XML%"
echo     ^</IdleSettings^> >> "%TASK_XML%"
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^> >> "%TASK_XML%"
echo     ^<Enabled^>true^</Enabled^> >> "%TASK_XML%"
echo     ^<Hidden^>false^</Hidden^> >> "%TASK_XML%"
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^> >> "%TASK_XML%"
echo     ^<WakeToRun^>false^</WakeToRun^> >> "%TASK_XML%"
echo     ^<ExecutionTimeLimit^>PT0S^</ExecutionTimeLimit^> >> "%TASK_XML%"
echo     ^<Priority^>7^</Priority^> >> "%TASK_XML%"
echo   ^</Settings^> >> "%TASK_XML%"
echo   ^<Actions Context="Author"^> >> "%TASK_XML%"
echo     ^<Exec^> >> "%TASK_XML%"
echo       ^<Command^>python^</Command^> >> "%TASK_XML%"
echo       ^<Arguments^>grafana_runner.py^</Arguments^> >> "%TASK_XML%"
echo       ^<WorkingDirectory^>%CURRENT_DIR%^</WorkingDirectory^> >> "%TASK_XML%"
echo     ^</Exec^> >> "%TASK_XML%"
echo   ^</Actions^> >> "%TASK_XML%"
echo ^</Task^> >> "%TASK_XML%"

:: Import the task
schtasks /create /tn "GrafanaRunner" /xml "%TASK_XML%" /f >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Could not create startup task automatically.
    echo You can manually add the task using Task Scheduler.
) else (
    echo ✅ Created Windows startup task: GrafanaRunner
)

:: Clean up temp file
del "%TASK_XML%" >nul 2>&1

echo.
echo ✅ Installation complete!
echo.
echo 📋 Next Steps:
echo 1. Edit config.json with your Grafana panel URLs
echo 2. Test the runner: python grafana_runner.py
echo    Or use: run.bat
echo 3. The startup task has been created and will run on user login
echo 4. To disable startup: schtasks /delete /tn "GrafanaRunner" /f
echo 5. To enable startup again: schtasks /change /tn "GrafanaRunner" /enable
echo.
echo 📖 For more information, see README.md
echo.
pause
