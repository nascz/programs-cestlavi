#!/usr/bin/env python3
"""
validar_instalacao.py
Script para validar se todas as dependências estão instaladas corretamente
Útil para debugging antes de usar o programa
"""

import sys
import subprocess

def check_python_version():
    """Verifica versão do Python"""
    print("\n[1/6] Verificando versão do Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (mínimo: 3.10)")
        return False

def check_module(module_name, import_name=None):
    """Verifica se um módulo está instalado"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def check_tesseract():
    """Verifica se Tesseract está instalado"""
    print("\n[6/6] Verificando Tesseract OCR...")
    try:
        result = subprocess.run(
            ["tesseract", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("❌ Tesseract não encontrado (essencial para OCR funcionar)")
    print("   Instale em: C:\\Program Files\\Tesseract-OCR\\")
    print("   Download: https://github.com/UB-Mannheim/tesseract/wiki")
    return False

def main():
    print("\n" + "="*70)
    print("  VALIDADOR DE INSTALAÇÃO - OCR_Documentos")
    print("="*70)
    
    checks = []
    
    # Check Python version
    checks.append(("Python 3.10+", check_python_version()))
    
    # Check modules
    modules = [
        ("customtkinter", "customtkinter"),
        ("pytesseract", "pytesseract"),
        ("Pillow", "PIL"),
        ("OpenCV", "cv2"),
        ("NumPy", "numpy"),
    ]
    
    for i, (name, import_name) in enumerate(modules, start=2):
        print(f"\n[{i}/6] Verificando {name}...", end=" ")
        if check_module(import_name):
            try:
                mod = __import__(import_name)
                version = getattr(mod, '__version__', 'desconhecida')
                print(f"✅ {version}")
                checks.append((name, True))
            except:
                print("✅")
                checks.append((name, True))
        else:
            print(f"❌ NÃO instalado")
            print(f"   Execute: pip install {name}")
            checks.append((name, False))
    
    # Check Tesseract
    checks.append(("Tesseract OCR", check_tesseract()))
    
    # Summary
    print("\n" + "="*70)
    print("  RESUMO")
    print("="*70)
    
    total = len(checks)
    passed = sum(1 for _, status in checks if status)
    
    for name, status in checks:
        symbol = "✅" if status else "❌"
        print(f"  {symbol} {name}")
    
    print(f"\nTotal: {passed}/{total} verificações passaram\n")
    
    if passed == total:
        print("🎉 TUDO OK! Você pode executar OCR_Documentos.exe")
    else:
        print("⚠️  Alguns componentes faltam. Execute:")
        print("   pip install -r requirements.txt")
        if not checks[-1][1]:  # Tesseract
            print("\n   E instale Tesseract em:")
            print("   https://github.com/UB-Mannheim/tesseract/wiki")
    
    print()
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
