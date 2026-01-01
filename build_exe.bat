@echo off
echo ========================================
echo Building WiFi Connector Executable
echo ========================================
echo.

REM Activar entorno virtual
echo Activando entorno virtual...
call .\venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    echo Asegurate de que existe la carpeta venv
    pause
    exit /b 1
)

REM Verificar PyInstaller en el venv
echo Checking PyInstaller en venv...
.\venv\Scripts\python.exe -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller en venv...
    .\venv\Scripts\python.exe -m pip install pyinstaller
)

REM Limpiar carpetas anteriores
echo.
echo Limpiando build anterior...
if exist build (
    echo Eliminando carpeta build...
    rmdir /s /q build
)
if exist dist (
    echo Eliminando carpeta dist...
    rmdir /s /q dist
)

REM Construir ejecutable
echo.
echo Building executable...
.\venv\Scripts\python.exe -m PyInstaller build_exe.spec --clean --noconfirm

REM Copiar carpeta Json a dist
echo.
echo Copiando carpeta Json a dist...
if exist Json (
    if not exist dist\Json (
        mkdir dist\Json
    )
    xcopy /y /i Json\*.json dist\Json\
    echo Archivos JSON copiados correctamente
) else (
    echo ADVERTENCIA: No se encontro la carpeta Json
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: dist\WifiEduca.exe
echo JSON files location: dist\Json\
echo.
pause
