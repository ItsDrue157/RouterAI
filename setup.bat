@echo off
chcp 65001 >nul
setlocal
title RouterAI - Primeira configuracao

set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
cd /d "%PROJECT_DIR%"

echo ======================================================
echo          RouterAI - Instalacao automatica
echo ======================================================
echo.

where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python nao foi encontrado.
        echo Instale o Python 3.10 ou mais recente e tente novamente.
        echo https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python"
)

echo [1/5] Verificando Python...
%PYTHON_CMD% --version
if errorlevel 1 goto :error
%PYTHON_CMD% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo [ERRO] O RouterAI precisa do Python 3.10 ou mais recente.
    goto :error
)
echo.

echo [2/5] Verificando uv...
%PYTHON_CMD% -m uv --version >nul 2>&1
if errorlevel 1 (
    echo uv nao encontrado. Instalando pelo PyPI...
    %PYTHON_CMD% -m pip --version >nul 2>&1
    if errorlevel 1 (
        %PYTHON_CMD% -m ensurepip --upgrade
        if errorlevel 1 goto :error
    )
    %PYTHON_CMD% -m pip install --user --upgrade uv
    if errorlevel 1 goto :error
)
%PYTHON_CMD% -m uv --version
echo.

echo [3/5] Criando o ambiente virtual...
if not exist ".venv\Scripts\python.exe" (
    %PYTHON_CMD% -m uv venv ".venv"
    if errorlevel 1 goto :error
) else (
    echo Ambiente .venv ja existe.
)
echo.

echo [4/5] Instalando as dependencias...
%PYTHON_CMD% -m uv pip install --python ".venv\Scripts\python.exe" -r "requirements.txt"
if errorlevel 1 goto :error
echo.

echo [5/5] Criando e verificando os bancos SQLite...
".venv\Scripts\python.exe" "db\banco.py"
if errorlevel 1 goto :error
echo.

echo ======================================================
echo  Configuracao concluida. Iniciando o RouterAI...
echo ======================================================
echo.
call "%PROJECT_DIR%\start.bat"
exit /b %errorlevel%

:error
echo.
echo ======================================================
echo [ERRO] A instalacao nao foi concluida.
echo Confira a mensagem acima e tente executar setup.bat novamente.
echo ======================================================
echo.
pause
exit /b 1
