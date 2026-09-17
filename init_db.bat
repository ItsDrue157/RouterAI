@echo off
chcp 65001 >nul
setlocal
title RouterAI - Inicializar bancos

set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
cd /d "%PROJECT_DIR%"

echo ======================================================
echo          RouterAI - Inicializacao dos bancos
echo ======================================================
echo.

if exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
) else if exist "%PROJECT_DIR%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_DIR%\venv\Scripts\python.exe"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python e ambiente virtual nao foram encontrados.
        echo Execute setup.bat primeiro.
        echo.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" "%PROJECT_DIR%\db\banco.py"
if errorlevel 1 (
    echo.
    echo [ERRO] Nao foi possivel inicializar os bancos.
    pause
    exit /b 1
)

echo.
echo Operacao concluida.
echo.
pause
