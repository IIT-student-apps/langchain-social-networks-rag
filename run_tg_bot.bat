@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo Starting Telegram bot...
python src\integrations\telegram_bot.py
if errorlevel 1 (
    echo.
    echo Bot exited with error. Press any key to close...
    pause >nul
)