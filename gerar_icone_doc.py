#!/usr/bin/env python3
"""
Script para criar uma imagem de documento (estilo DOC) para usar como ícone
"""

from PIL import Image, ImageDraw, ImageFont
import os

def criar_icone_documento():
    """Cria uma imagem de documento com estilo DOC"""
    
    # Tamanho da imagem
    tamanho = 512
    img = Image.new('RGB', (tamanho, tamanho), color='white')
    draw = ImageDraw.Draw(img)
    
    # Cores
    cor_azul = '#4A90E2'
    cor_cinza = '#CCCCCC'
    cor_texto = '#333333'
    
    # Fundo branco
    draw.rectangle([(0, 0), (tamanho, tamanho)], fill='white')
    
    # Borda cinza
    draw.rectangle([(20, 20), (tamanho-20, tamanho-20)], outline=cor_cinza, width=3)
    
    # Parte azul no topo (como um header)
    draw.rectangle([(40, 40), (tamanho-40, 120)], fill=cor_azul)
    
    # Ícone de documento (pequenos quadrados azuis)
    quad_size = 30
    spacing = 20
    x_pos = 70
    y_pos = 50
    
    for i in range(2):
        draw.rectangle(
            [(x_pos + i*(quad_size + spacing), y_pos), 
             (x_pos + i*(quad_size + spacing) + quad_size, y_pos + quad_size)],
            fill='white', outline='white'
        )
    
    # Linhas de texto cinzas
    line_height = 40
    start_y = 160
    line_color = cor_cinza
    
    for i in range(5):
        y = start_y + (i * line_height)
        width = tamanho - 80 if i != 0 else tamanho - 120
        draw.rectangle([(50, y), (50 + width, y + 15)], fill=line_color)
    
    # Texto "DOC" em azul
    try:
        # Tentar usar uma fonte maior
        font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 80)
    except:
        # Fallback para fonte padrão
        font = ImageFont.load_default()
    
    text = "DOC"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x_text = (tamanho - text_width) // 2
    y_text = tamanho - 100
    
    draw.text((x_text, y_text), text, fill=cor_azul, font=font)
    
    # Salvar
    output_path = os.path.join(os.path.dirname(__file__), 'icone_documento.png')
    img.save(output_path, 'PNG')
    print(f"✅ Ícone criado: {output_path}")
    return output_path

if __name__ == "__main__":
    criar_icone_documento()
