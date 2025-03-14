@echo off
echo Running setup script...

REM Check if Git Bash is installed
where bash >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Git Bash is not installed. Please install Git for Windows.
    echo Visit: https://git-scm.com/download/win
    exit /b 1
)

REM Run the setup script
bash setup.sh

if %ERRORLEVEL% NEQ 0 (
    echo Setup failed!
    exit /b 1
)

echo Setup completed successfully! 