@echo off
:: Grafana Runner Startup Script
:: This script pulls the latest changes and starts the application

:: Set working directory to script location
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"
cd /d "%CURRENT_DIR%"

:: Create log file if it doesn't exist
if not exist "%CURRENT_DIR%\runner.log" (
    echo. > "%CURRENT_DIR%\runner.log"
)

:: Log startup with debug info
echo [%date% %time%] Starting GrafanaRunner startup script... >> "%CURRENT_DIR%\runner.log" 2>&1
echo [%date% %time%] Working directory: %CURRENT_DIR% >> "%CURRENT_DIR%\runner.log" 2>&1
echo [%date% %time%] PATH: %PATH% >> "%CURRENT_DIR%\runner.log" 2>&1

:: Find Python executable with error handling
set "PYTHON_EXE="
python --version >> "%CURRENT_DIR%\runner.log" 2>&1
if errorlevel 1 (
    echo [%date% %time%] ERROR: Python not found in PATH >> "%CURRENT_DIR%\runner.log" 2>&1
    :: Try common Python locations
    if exist "C:\Python*\python.exe" (
        for /f "delims=" %%P in ('dir /b "C:\Python*\python.exe" 2^>nul') do set "PYTHON_EXE=C:\%%P"
    )
    if exist "%LOCALAPPDATA%\Programs\Python\Python*\python.exe" (
        for /f "delims=" %%P in ('dir /b "%LOCALAPPDATA%\Programs\Python\Python*\python.exe" 2^>nul') do set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\%%P"
    )
) else (
    for /f "usebackq delims=" %%P in (`python -c "import sys; print(sys.executable)" 2^>nul`) do (
        set "PYTHON_EXE=%%P"
    )
)

if "%PYTHON_EXE%"=="" (
    echo [%date% %time%] ERROR: Could not find Python executable >> "%CURRENT_DIR%\runner.log" 2>&1
    exit /b 1
)

echo [%date% %time%] Using Python: %PYTHON_EXE% >> "%CURRENT_DIR%\runner.log" 2>&1

:: Check if git is available and pull latest changes
echo [%date% %time%] Checking for git... >> "%CURRENT_DIR%\runner.log" 2>&1
git --version >> "%CURRENT_DIR%\runner.log" 2>&1
if errorlevel 1 (
    echo [%date% %time%] WARNING: Git not found in PATH, skipping git pull >> "%CURRENT_DIR%\runner.log" 2>&1
) else (
    echo [%date% %time%] Pulling latest changes... >> "%CURRENT_DIR%\runner.log" 2>&1
    git pull >> "%CURRENT_DIR%\runner.log" 2>&1
    echo [%date% %time%] Git pull completed >> "%CURRENT_DIR%\runner.log" 2>&1
)

:: Start the application
echo [%date% %time%] Starting Grafana Runner application... >> "%CURRENT_DIR%\runner.log" 2>&1
"%PYTHON_EXE%" "%CURRENT_DIR%\grafana_runner.py" >> "%CURRENT_DIR%\runner.log" 2>&1
