@echo off
SETLOCAL

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)

:: Install requirements
echo Installing required Python packages...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install Python packages. Please check your Python and pip setup.
    pause
    exit /b
)

:: Check if ollama is installed
echo Checking if Ollama is installed...
ollama --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Ollama is not installed.
    echo Redirecting you to the Ollama installation page...
    start https://ollama.com/download
    pause
    exit /b
)

:: Start the Flask application
echo Starting Flask application...
start http://127.0.0.1:5000
python justaui.py

ENDLOCAL
