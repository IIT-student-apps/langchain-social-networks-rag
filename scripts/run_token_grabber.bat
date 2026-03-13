@echo off
cd ..
call "venv\Scripts\activate.bat"
echo Starting VK Token Grabber...
echo Browser will open - log in to VK to capture access token.
echo Token will be saved automatically to .env
echo.
python "scripts\token_grabber.py"
if errorlevel 1 (
    echo.
    echo Token grabber exited with error. Press any key to close...
    pause >nul
)
