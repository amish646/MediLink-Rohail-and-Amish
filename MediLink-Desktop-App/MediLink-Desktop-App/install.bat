@echo off
cd /d "%~dp0"
echo ===================================================
echo   Installing MediLink Desktop App...
echo ===================================================
echo.
echo Step 1: Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Dependency installation failed.
    echo Please make sure Python is installed and added to PATH.
    pause
    exit /b %errorlevel%
)

echo.
echo Step 2: Creating Desktop Shortcut...
powershell -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1"
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Failed to create desktop shortcut automatically.
    echo You can create it manually by right-clicking launch.bat.
) else (
    echo.
    echo SUCCESS: Desktop shortcut created successfully with MediLink branding!
)

echo.
echo ===================================================
echo   Installation Completed Successfully!
echo ===================================================
pause
