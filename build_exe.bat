@echo off
echo ========================================
echo Building WiFi Connector Executable
echo ========================================
echo.

REM Install PyInstaller if not already installed
echo Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
) else (
    echo PyInstaller already installed
)

echo.
echo Building executable...
pyinstaller --clean build_exe.spec

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: dist\WiFiConnector.exe
echo.
pause
