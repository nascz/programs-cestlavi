# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file para OCR GUI

block_cipher = None

import glob

a = Analysis(
    ['cdigo\\ocr_launcher.py'],
    pathex=['.'],
    binaries=[],
    # include all python sources from the cdigo package so the built EXE contains the latest code
    datas=[(f, 'cdigo') for f in glob.glob('cdigo\\*.py')],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'cv2',
        'pytesseract',
        'numpy',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OCR_Documentos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = sem console, True = com console
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico',  # Usar o ícone criado
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OCR_Documentos',
)

import shutil
import os

# Copy EXE to project root after build
if __name__ == '__main__':
    dist_exe = os.path.join('cdigo', 'dist', 'OCR_Documentos', 'OCR_Documentos.exe')
    root_exe = 'OCR_Documentos.exe'
    if os.path.exists(dist_exe):
        try:
            shutil.copy2(dist_exe, root_exe)
            print(f"\n✅ EXE copiado para: {os.path.abspath(root_exe)}")
        except Exception as e:
            print(f"\n⚠️ Não foi possível copiar EXE: {e}")
