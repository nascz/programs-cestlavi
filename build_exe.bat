@echo off
REM Script para reconstruir o EXE OCR
REM Use: build_exe.bat

setlocal enabledelayedexpansion

REM Parar qualquer EXE em execução
taskkill /IM OCR_Documentos.exe /F 2>nul

REM Ativar venv e rodar PyInstaller
call .venv\Scripts\activate.bat
echo.
echo 🔨 Construindo EXE...
pyinstaller .\ocr.spec --noconfirm --clean

REM Copiar EXE para raiz
if exist "dist\OCR_Documentos.exe" (
    copy /Y "dist\OCR_Documentos.exe" "OCR_Documentos.exe" >nul
    for /F %%A in ('powershell -Command "(Get-Item 'OCR_Documentos.exe').Length / 1MB | ForEach-Object { [math]::Round($_, 1) }"') do set SIZE=%%A
    echo.
    echo ✅ EXE atualizado na raiz (!SIZE! MB)
    echo 📁 Local: %cd%\OCR_Documentos.exe
) else (
    echo ❌ Falha ao reconstruir EXE
    pause
)

pause
