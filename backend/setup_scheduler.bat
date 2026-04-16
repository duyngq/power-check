@echo off
REM =====================================================
REM Setup Windows Task Scheduler for Power Outage Checker
REM Chạy script này với quyền Administrator
REM =====================================================

set SCRIPT_PATH=%~dp0scheduler.py
set PYTHON_PATH=python

echo Creating scheduled tasks for Power Outage Checker...
echo Script path: %SCRIPT_PATH%

REM Task 1: Chạy lúc 00:00 (12AM) hàng ngày
schtasks /create /tn "PowerOutageCheck_Midnight" /tr "cmd /c cd /d %~dp0 && %PYTHON_PATH% scheduler.py" /sc daily /st 00:00 /f
if %errorlevel% equ 0 (
    echo [OK] Task "PowerOutageCheck_Midnight" created successfully (00:00 daily)
) else (
    echo [ERROR] Failed to create midnight task
)

REM Task 2: Chạy lúc 06:00 (6AM) hàng ngày
schtasks /create /tn "PowerOutageCheck_Morning" /tr "cmd /c cd /d %~dp0 && %PYTHON_PATH% scheduler.py" /sc daily /st 06:00 /f
if %errorlevel% equ 0 (
    echo [OK] Task "PowerOutageCheck_Morning" created successfully (06:00 daily)
) else (
    echo [ERROR] Failed to create morning task
)

echo.
echo =====================================================
echo Setup completed!
echo.
echo To view tasks: schtasks /query /tn "PowerOutageCheck*"
echo To delete tasks:
echo   schtasks /delete /tn "PowerOutageCheck_Midnight" /f
echo   schtasks /delete /tn "PowerOutageCheck_Morning" /f
echo =====================================================

pause
