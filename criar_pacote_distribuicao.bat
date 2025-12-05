@echo off
REM Script para criar pacote de distribuicao do OCR_Documentos

cls
color 0A
title Criador de Pacote de Distribuicao

echo.
echo ============================================================================
echo  Criador de Pacote - OCR_Documentos
echo ============================================================================
echo.

REM Verifica se 7-Zip ou WinRAR estao instalados
set compressor=

REM Tenta 7-Zip
if exist "C:\Program Files\7-Zip\7z.exe" (
    set "compressor=C:\Program Files\7-Zip\7z.exe"
    set compressor_name=7-Zip
    goto found_compressor
)

if exist "C:\Program Files (x86)\7-Zip\7z.exe" (
    set "compressor=C:\Program Files (x86)\7-Zip\7z.exe"
    set compressor_name=7-Zip
    goto found_compressor
)

REM Tenta WinRAR
if exist "C:\Program Files\WinRAR\WinRAR.exe" (
    set "compressor=C:\Program Files\WinRAR\WinRAR.exe"
    set compressor_name=WinRAR
    goto found_compressor
)

:not_found_compressor
echo [AVISO] Nenhum compressor encontrado
echo.
echo Para criar um ZIP, instale um dos:
echo - 7-Zip: https://www.7-zip.org/
echo - WinRAR: https://www.rarlab.com/
echo.
echo Criando ZIP com PowerShell...
echo.

REM Usa PowerShell para compactar
set timestamp=%date:~-4%-%date:~-10,2%-%date:~-7,2%_%time:~0,2%-%time:~3,2%
set timestamp=%timestamp: =0%
set zipfile=OCR_Documentos_%timestamp%.zip

powershell -Command "& {Add-Type -A System.IO.Compression.FileSystem; [IO.Compression.ZipFile]::CreateFromDirectory('.', '%zipfile%')}"

if exist %zipfile% (
    echo [OK] Pacote criado: %zipfile%
    echo Tamanho: 
    for /f %%A in ('dir /b "%zipfile%"') do echo %%~zA bytes
) else (
    echo [ERRO] Falha ao criar ZIP
)

pause
exit /b 0

:found_compressor
echo [OK] Compressor encontrado: %compressor_name%
echo.

REM Criar arquivo de resposta
set zipfile=OCR_Documentos.zip

if exist "%zipfile%" (
    del "%zipfile%"
    echo [OK] Arquivo anterior removido
)

echo Compactando arquivos...

if "%compressor_name%"=="7-Zip" (
    "%compressor%" a -tzip "%zipfile%" ^
        "OCR_Documentos.exe" ^
        "install_dependencies.bat" ^
        "requirements.txt" ^
        "README.md" ^
        "README_MODULAR.md" ^
        "START_HERE.txt" ^
        "DISTRIBUIR.md" ^
        "app.ico"
) else (
    "%compressor%" a -ep1 "%zipfile%" ^
        "OCR_Documentos.exe" ^
        "install_dependencies.bat" ^
        "requirements.txt" ^
        "README.md" ^
        "README_MODULAR.md" ^
        "START_HERE.txt" ^
        "DISTRIBUIR.md" ^
        "app.ico"
)

if exist "%zipfile%" (
    echo.
    color 0A
    echo [OK] SUCESSO!
    echo.
    echo Arquivo criado: %zipfile%
    echo.
    echo Conteudo do pacote:
    echo - OCR_Documentos.exe (programa executavel)
    echo - install_dependencies.bat (instalador automatico)
    echo - requirements.txt (dependencias Python)
    echo - *.md (documentacao)
    echo - app.ico (icone)
    echo.
    echo Proximas instrucoes:
    echo 1. Envie %zipfile% por email ou pen drive
    echo 2. O usuario extrai e abre install_dependencies.bat
    echo 3. Pronto! Programa estara funcionando em 5-10 minutos
    echo.
) else (
    color 0C
    echo [ERRO] Falha ao compactar
)

pause
