@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Webhook (Power Automate)...
start "Webhook Power Automate" cmd /k "py -3 services\webhook_server.py"
timeout /t 2 >nul

echo [3/3] Iniciando Streamlit e Navegador...
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause
