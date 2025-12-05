#!/usr/bin/env python3
"""
Script para reconstruir o EXE OCR de forma rápida.
Use: python build_exe.py
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path

def build():
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    venv_activate = project_root / ".venv" / "Scripts" / "activate.bat"
    spec_file = project_root / "ocr.spec"
    
    if not venv_activate.exists():
        print("❌ Ambiente virtual não encontrado")
        return False
    
    print("🔨 Construindo EXE...")
    try:
        if sys.platform == "win32":
            subprocess.run([str(venv_activate), "&&", "pyinstaller", str(spec_file), "--noconfirm", "--clean"], shell=True, check=True)
        else:
            subprocess.run([str(venv_activate), "&&", "pyinstaller", str(spec_file), "--noconfirm", "--clean"], shell=True, check=True)
        
        dist_exe = project_root / "cdigo" / "dist" / "OCR_Documentos" / "OCR_Documentos.exe"
        root_exe = project_root / "OCR_Documentos.exe"
        
        if dist_exe.exists():
            shutil.copy2(dist_exe, root_exe)
            print(f"✅ EXE atualizado: {root_exe}")
            print(f"📁 Tamanho: {root_exe.stat().st_size / 1024 / 1024:.1f} MB")
            return True
        else:
            print("❌ EXE não encontrado após build")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
