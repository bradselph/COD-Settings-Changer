@echo off
cd /d "%~dp0"
python build.py
echo.
echo Script execution complete. Press any key to close.
pause > nul
