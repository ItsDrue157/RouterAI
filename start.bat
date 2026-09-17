@echo off
chcp 65001 >nul
setlocal
title RouterAI - Inicializador

set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
cd /d "%PROJECT_DIR%"

echo ======================================================
echo              RouterAI - Inicializador
echo ======================================================
echo.

if exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
) else if exist "%PROJECT_DIR%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_DIR%\venv\Scripts\python.exe"
) else (
    echo [ERRO] Ambiente virtual nao encontrado.
    echo Execute setup.bat antes de iniciar o projeto.
    echo.
    pause
    exit /b 1
)

if exist "%PROJECT_DIR%\frontend\index.html" (
    set "FRONTEND_DIR=%PROJECT_DIR%\frontend"
) else if exist "%PROJECT_DIR%\RouterAI- frontend\index.html" (
    set "FRONTEND_DIR=%PROJECT_DIR%\RouterAI- frontend"
) else if exist "%PROJECT_DIR%\..\RouterAI- frontend\index.html" (
    set "FRONTEND_DIR=%PROJECT_DIR%\..\RouterAI- frontend"
) else (
    echo [ERRO] Frontend nao encontrado.
    echo Coloque os arquivos em frontend ou em "RouterAI- frontend".
    echo.
    pause
    exit /b 1
)

echo [1/4] Verificando os bancos SQLite...
"%PYTHON_EXE%" "%PROJECT_DIR%\db\banco.py"
if errorlevel 1 (
    echo [ERRO] Nao foi possivel inicializar os bancos.
    pause
    exit /b 1
)
echo.

echo [2/4] Verificando o servidor do LM Studio...
powershell -NoProfile -Command "try { $null = Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:1234/v1/models' -TimeoutSec 3; exit 0 } catch { exit 1 }"
if errorlevel 1 (
    echo [AVISO] O servidor do LM Studio nao respondeu na porta 1234.
    echo O RouterAI vai abrir, mas as mensagens so funcionarao depois que o servidor estiver ativo.
    echo Execute setup_models.bat ou inicie o servidor pelo LM Studio.
) else (
    echo Servidor do LM Studio encontrado.
)
echo.

echo [3/4] Iniciando a API em http://127.0.0.1:8000 ...
start "RouterAI - Backend" /D "%PROJECT_DIR%" cmd /k ""%PYTHON_EXE%" -m fastapi dev main.py"

echo [4/4] Iniciando o frontend em http://127.0.0.1:5000 ...
start "RouterAI - Frontend" /D "%FRONTEND_DIR%" cmd /k ""%PYTHON_EXE%" -m http.server 5000 --bind 127.0.0.1"

echo.
echo ======================================================
echo  RouterAI iniciado:
echo   - Frontend: http://127.0.0.1:5000
echo   - API:      http://127.0.0.1:8000
echo   - Swagger:  http://127.0.0.1:8000/docs
echo ======================================================
echo Feche as duas janelas dos servidores para encerrar.
echo.
pause
