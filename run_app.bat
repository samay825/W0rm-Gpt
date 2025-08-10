@echo off
echo ========================================
echo Black Worm Application Launcher
echo ========================================


python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Checking Python packages...

python -c "import PyQt5" >nul 2>&1
set PYQT5_INSTALLED=%errorlevel%


python -c "import requests" >nul 2>&1
set REQUESTS_INSTALLED=%errorlevel%


if %PYQT5_INSTALLED% neq 0 (
    echo PyQt5 not found, installing...
    pip install PyQt5>=5.15.10
) else (
    echo PyQt5 is already installed
)

if %REQUESTS_INSTALLED% neq 0 (
    echo requests not found, installing...
    pip install requests>=2.31.0
) else (
    echo requests is already installed
)


echo Verifying all packages are installed...
python -c "import PyQt5, requests" >nul 2>&1
if errorlevel 1 (
    echo Error: Failed to install required packages
    echo Trying to install from requirements.txt...
    pip install -r requirements.txt
    
    
    python -c "import PyQt5, requests" >nul 2>&1
    if errorlevel 1 (
        echo Error: Still unable to import required packages
        pause
        exit /b 1
    )
)

echo All packages are ready!
echo ========================================
echo Starting Black Worm Application...
echo ========================================


python main.py


if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)