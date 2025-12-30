@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Creating virtual environment...
python -m venv venv

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to create venv. Make sure Python is installed and in PATH.
    pause
    exit
)

echo [2/3] Activating environment and upgrading pip...
call venv\Scripts\activate
python -m pip install --upgrade pip

echo [3/3] Installing dependencies from requirements.txt...
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit
)

echo.
echo ======================================================
echo [SUCCESS] Environment is ready!
echo You can now run the app using run_app.bat
echo ======================================================
echo.
pause
