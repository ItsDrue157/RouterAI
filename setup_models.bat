@echo off
chcp 65001 >nul
setlocal
title RouterAI - Modelos do LM Studio

echo ======================================================
echo          RouterAI - Configuracao dos modelos
echo ======================================================
echo.

set "LMS_EXE=%USERPROFILE%\.lmstudio\bin\lms.exe"
if exist "%LMS_EXE%" goto :lms_found

where lms >nul 2>&1
if not errorlevel 1 (
    set "LMS_EXE=lms"
    goto :lms_found
)

echo [ERRO] O comando lms nao foi encontrado.
echo.
echo Instale e abra o LM Studio pelo menos uma vez:
echo https://lmstudio.ai/download
echo.
echo Depois execute este script novamente.
pause
exit /b 1

:lms_found
echo Este script vai baixar os modelos usados pelo RouterAI.
echo O LM Studio pode pedir que voce escolha uma quantizacao.
echo.

echo [1/3] Baixando o modelo roteador...
"%LMS_EXE%" get qwen/qwen3-1.7b
if errorlevel 1 goto :error
echo.

echo [2/3] Baixando o modelo de resposta...
"%LMS_EXE%" get qwen/qwen3-4b-2507
if errorlevel 1 goto :error
echo.

echo [3/3] Iniciando o servidor local na porta 1234...
"%LMS_EXE%" server start --port 1234
if errorlevel 1 (
    echo [AVISO] Nao foi possivel iniciar o servidor automaticamente.
    echo Ele pode ja estar rodando. Confira o LM Studio.
)

echo.
echo Modelos preparados.
echo Agora execute setup.bat ou start.bat.
echo.
pause
exit /b 0

:error
echo.
echo [ERRO] O download nao foi concluido.
echo Confira a mensagem acima e tente novamente.
echo.
pause
exit /b 1
