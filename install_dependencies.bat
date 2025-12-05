@echo off
REM ============================================================================
REM Script para instalar todas as dependências do OCR_Documentos
REM ============================================================================
REM Este script:
REM 1. Instala Python packages (pip install -r requirements.txt)
REM 2. Baixa e instala Tesseract OCR (v5.x)
REM 3. Valida a instalação
REM ============================================================================

cls
color 0A
title Instalador de Dependencias - OCR_Documentos

echo.
echo ============================================================================
echo  INSTALADOR - OCR_Documentos v1.0
echo ============================================================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERRO] Python nao foi encontrado no PATH
    echo.
    echo Instale Python 3.10+ de: https://www.python.org
    echo Durante a instalacao, MARQUE "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Mostra versão do Python
echo [OK] Python detectado:
python --version
echo.

REM ============================================================================
REM Passo 1: Instalar pacotes Python
REM ============================================================================
echo Passo 1/3: Instalando pacotes Python...
echo ============================================================================
if exist requirements.txt (
    pip install --upgrade pip -q
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [ERRO] Falha ao instalar pacotes Python
        pause
        exit /b 1
    )
    echo [OK] Pacotes Python instalados com sucesso
) else (
    color 0C
    echo [ERRO] requirements.txt nao encontrado
    pause
    exit /b 1
)
echo.

REM ============================================================================
REM Passo 2: Instalar Tesseract OCR
REM ============================================================================
echo Passo 2/3: Verificando Tesseract OCR...
echo ============================================================================

tesseract --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Tesseract ja esta instalado:
    tesseract --version
    echo.
) else (
    echo [AVISO] Tesseract OCR nao foi encontrado
    echo.
    echo O Tesseract é necessario para o programa funcionar.
    echo.
    echo Opcoes de instalacao:
    echo.
    echo 1) Instalacao AUTOMATICA (recomendado):
    echo    - Precisa de conexao com internet
    echo    - Requer permissoes de administrador
    echo.
    echo 2) Instalacao MANUAL:
    echo    - Baixe em: https://github.com/UB-Mannheim/tesseract/wiki
    echo    - Procure por: tesseract-ocr-w64-setup-v5.x.exe
    echo    - Instale em: C:\Program Files\Tesseract-OCR
    echo.
    echo Deseja fazer download e instalar AUTOMATICAMENTE? (S/N)
    set /p choice="Resposta: "
    
    if /i "%choice%"=="S" (
        color 0B
        echo.
        echo Baixando Tesseract OCR v5.4.1...
        echo Isto pode levar alguns minutos...
        echo.
        
        REM Baixa o instalador (pode customizar a versao)
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.1/tesseract-ocr-w64-setup-v5.4.1.exe', 'tesseract-installer.exe')}"
        
        if exist tesseract-installer.exe (
            echo [OK] Download completo
            echo.
            echo Iniciando instalacao do Tesseract...
            tesseract-installer.exe /S /D=C:\Program Files\Tesseract-OCR
            
            REM Aguarda a instalacao
            timeout /t 5 /nobreak
            
            REM Limpa o instalador
            del tesseract-installer.exe
            
            REM Valida
            tesseract --version >nul 2>&1
            if %ERRORLEVEL% EQU 0 (
                echo [OK] Tesseract instalado com sucesso!
                tesseract --version
            ) else (
                color 0C
                echo [ERRO] Tesseract nao foi instalado corretamente
                echo Tente instalacao manual: https://github.com/UB-Mannheim/tesseract/wiki
                pause
            )
        ) else (
            color 0C
            echo [ERRO] Nao foi possivel baixar o Tesseract
            echo Tente instalacao manual: https://github.com/UB-Mannheim/tesseract/wiki
            pause
        )
    ) else (
        echo.
        echo [AVISO] Tesseract nao sera instalado
        echo O programa NAO funcionara sem o Tesseract
        echo.
    )
)
echo.

REM ============================================================================
REM Passo 3: Validacao
REM ============================================================================
echo Passo 3/3: Validando instalacao...
echo ============================================================================
echo.

python -c "import customtkinter; print('[OK] customtkinter instalado')" 2>nul || echo [ERRO] customtkinter nao instalado
python -c "import pytesseract; print('[OK] pytesseract instalado')" 2>nul || echo [ERRO] pytesseract nao instalado
python -c "import PIL; print('[OK] Pillow instalado')" 2>nul || echo [ERRO] Pillow nao instalado
python -c "import cv2; print('[OK] OpenCV instalado')" 2>nul || echo [ERRO] OpenCV nao instalado
python -c "import numpy; print('[OK] NumPy instalado')" 2>nul || echo [ERRO] NumPy nao instalado

echo.
tesseract --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Tesseract OCR detectado
    tesseract --version
    echo.
    color 0A
    echo ============================================================================
    echo  SUCESSO! Todas as dependencias foram instaladas.
    echo ============================================================================
    echo.
    echo Proximos passos:
    echo 1. Execute: OCR_Documentos.exe
    echo 2. Carregue uma imagem com texto
    echo 3. Clique em "Processar" para testar a OCR
    echo.
) else (
    color 0C
    echo [ERRO] Tesseract OCR nao foi detectado!
    echo.
    echo O programa nao funcionara sem o Tesseract.
    echo Instale manualmente em: C:\Program Files\Tesseract-OCR
    echo Download: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
)

pause
