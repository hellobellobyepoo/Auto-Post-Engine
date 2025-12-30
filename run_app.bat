@echo off
setlocal
cd /d "%~dp0"

echo [DEBUG] Current Directory: %CD%

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Python not found in venv. 
    echo Please run install_deps.bat again.
    pause
    exit
)

echo [DEBUG] Activating VENV...
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Activation failed.
    pause
    exit
)

echo [DEBUG] Starting App...
python main.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python process exited with code %ERRORLEVEL%
)

echo.
echo [DEBUG] Script end.
pause
