@echo off
setlocal
title TikTok Streak Auto-Saver & Helper Hub

:: Check if python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Python 3 tidak ditemukan di sistem Anda!
        echo Silakan instal Python dari https://www.python.org/
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

:: Setup local venv if not exists
if not exist "%USERPROFILE%\.tiktok-streak\venv" (
    echo [*] Menyiapkan lingkungan awal...
    %PYTHON_CMD% -m venv "%USERPROFILE%\.tiktok-streak\venv"
    call "%USERPROFILE%\.tiktok-streak\venv\Scripts\activate.bat"
    pip install playwright requests
    playwright install chromium
) else (
    call "%USERPROFILE%\.tiktok-streak\venv\Scripts\activate.bat"
)

:: Run interactive hub
python "%~dp0tiktok-streak.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Exited with code %ERRORLEVEL%.
    pause
)
