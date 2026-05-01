@echo off
setlocal EnableExtensions

chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

cd /d "%~dp0"

if not exist "main.py" (
    echo [error] main.py was not found.
    echo Put START.bat in the project folder and run it from there.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo [setup] Creating virtual environment...
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 -m venv venv
    ) else (
        python -m venv venv
    )
    if errorlevel 1 goto setup_failed
)

if not exist ".env" (
    if exist ".env.example" (
        echo [setup] Creating .env from .env.example...
        copy ".env.example" ".env" >nul
    )
)

if exist "requirements.txt" (
    "venv\Scripts\python.exe" -c "import hashlib, pathlib, sys; req=pathlib.Path('requirements.txt'); marker=pathlib.Path('venv/.requirements.sha256'); current=hashlib.sha256(req.read_bytes()).hexdigest(); sys.exit(0 if marker.exists() and marker.read_text(encoding='ascii').strip()==current else 1)"
    if errorlevel 1 (
        echo [setup] Installing dependencies...
        "venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
        if errorlevel 1 goto setup_failed
        "venv\Scripts\python.exe" -c "import hashlib, pathlib; req=pathlib.Path('requirements.txt'); marker=pathlib.Path('venv/.requirements.sha256'); marker.write_text(hashlib.sha256(req.read_bytes()).hexdigest(), encoding='ascii')"
        if errorlevel 1 goto setup_failed
    )
)

echo [run] Starting application...
"venv\Scripts\python.exe" main.py %*
set "APP_EXIT_CODE=%ERRORLEVEL%"

if not "%APP_EXIT_CODE%"=="0" (
    echo.
    echo [error] Application exited with code %APP_EXIT_CODE%.
    pause
)

exit /b %APP_EXIT_CODE%

:setup_failed
echo.
echo [error] Setup failed. Check the messages above.
pause
exit /b 1
