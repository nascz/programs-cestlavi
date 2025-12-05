#!/usr/bin/env python3
"""
Script para converter uma imagem em ícone do Windows (.ico)
Uso: python criar_icone.py caminho_da_imagem.png
"""

from PIL import Image
import sys
import os

def criar_icone(caminho_imagem, caminho_saida='app.ico'):
    """Converte uma imagem em ícone .ico"""
    try:
        # Abrir imagem
        img = Image.open(caminho_imagem)
        
        # Redimensionar para tamanhos padrão de ícone
        # Windows suporta múltiplos tamanhos em um único .ico
        tamanhos = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
        
        # Converter para RGBA se necessário
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Redimensionar para cada tamanho
        imagens = []
        for tamanho in tamanhos:
            img_redimensionada = img.resize(tamanho, Image.Resampling.LANCZOS)
            imagens.append(img_redimensionada)
        
        # Salvar como .ico
        imagens[0].save(
            caminho_saida,
            format='ICO',
            sizes=tamanhos,
            icon_sizes=tamanhos
        )
        
        print(f"✅ Ícone criado com sucesso: {caminho_saida}")
        print(f"📦 Tamanhos inclusos: {tamanhos}")
        return True
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {caminho_imagem}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python criar_icone.py <caminho_da_imagem.png> [nome_saida.ico]")
        print("\nExemplo:")
        print("  python criar_icone.py meu_documento.png")
        print("  python criar_icone.py meu_documento.png app.ico")
        sys.exit(1)
    
    caminho_img = sys.argv[1]
    caminho_ico = sys.argv[2] if len(sys.argv) > 2 else 'app.ico'
    
    criar_icone(caminho_img, caminho_ico)
