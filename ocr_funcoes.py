# ocr_funcoes.py - Funções de processamento OCR
import pytesseract
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os
import cv2
import numpy as np

from tesseract_config import apply_to_environment

# Ensure we have consistent TESSDATA_PREFIX and pytesseract settings across modules
apply_to_environment()

def processar_imagem(nome_arquivo, imagens_dir):
    """
    Processa uma imagem e extrai texto usando OCR
    """
    try:
        # Caminho completo da imagem
        caminho_imagem = os.path.join(imagens_dir, nome_arquivo)
        
        # Verificar se arquivo existe
        if not os.path.exists(caminho_imagem):
            print(f"❌ Arquivo não encontrado: {caminho_imagem}")
            return None
        
        # Verificar se arquivo é válido (tamanho > 0)
        if os.path.getsize(caminho_imagem) == 0:
            print(f"❌ Arquivo vazio: {nome_arquivo}")
            return None
        
        print(f"🔄 Processando: {nome_arquivo}")
        
        # Pré-processamento da imagem (retorna PIL.Image)
        imagem_processada = preprocessar_imagem(caminho_imagem)
        
        if imagem_processada is None:
            print(f"❌ Não foi possível processar a imagem: {nome_arquivo}")
            return None

        # Configurações do Tesseract otimizadas para português
        # PSM 3 = segmentação automática (melhor para documentos)
        config = '--oem 3 --psm 3 -l por'

        # Extrair texto (garantir que é PIL.Image)
        texto = pytesseract.image_to_string(imagem_processada, config=config)
        
        print(f"✅ Concluído: {nome_arquivo}")
        return texto.strip()
        
    except Exception as e:
        print(f"❌ Erro ao processar {nome_arquivo}: {e}")
        return None

def preprocessar_imagem(caminho_imagem):
    """
    Melhora a qualidade da imagem para melhor OCR
    """
    try:
        # Ler imagem com cv2
        imagem = cv2.imread(caminho_imagem)

        # Verificar se a imagem foi carregada
        if imagem is None:
            print(f"⚠️ cv2 não conseguiu ler a imagem, tentando PIL...")
            try:
                pil = Image.open(caminho_imagem)
                # Validar que a imagem é válida
                pil.verify()
                pil = Image.open(caminho_imagem)  # Reabrir após verify
                pil = pil.convert('L')
                pil = ImageOps.autocontrast(pil, cutoff=2)
                pil = pil.filter(ImageFilter.SHARPEN)
                return pil
            except Exception as e:
                print(f"⚠️ PIL também falhou: {e}")
                return None

        # Converter para RGB e criar PIL image
        rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)

        # Converter para escala de cinza, aumentar contraste e aplicar sharpen
        pil = pil.convert('L')
        pil = ImageOps.autocontrast(pil, cutoff=2)
        pil = pil.filter(ImageFilter.SHARPEN)

        return pil
        
    except Exception as e:
        print(f"⚠️ Erro fatal no pré-processamento: {e}")
        return None

def criar_imagem_teste():
    """
    Cria uma imagem de teste simulando um documento
    """
    try:
        # Definir caminho da imagem (será criada na pasta imagens da raiz)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        imagens_dir = os.path.join(project_root, "imagens")
        os.makedirs(imagens_dir, exist_ok=True)
        # Criar imagem branca (maior para melhor OCR)
        img = Image.new('RGB', (1600, 1000), color='white')
        d = ImageDraw.Draw(img)

        # Tentar usar uma fonte do sistema para melhor legibilidade
        fonte = None
        possiveis_fontes = [r"C:\\Windows\\Fonts\\arial.ttf", r"C:\\Windows\\Fonts\\calibri.ttf", "arial.ttf"]
        for fpath in possiveis_fontes:
            try:
                fonte = ImageFont.truetype(fpath, 36)
                break
            except Exception:
                fonte = None
        if fonte is None:
            fonte = ImageFont.load_default()
        
        # Texto de teste (documento fictício)
        texto = """DOCUMENTO DE IDENTIFICACAO
Nome: Maria Oliveira Santos
CPF: 987.654.321-00
RG: 12.345.678-9
Data de Nascimento: 20/07/1985
Orgao Emissor: SSP-MT
Cidade: Barra do Bugres-MT

INFORMACOES DO SISTEMA OCR:
Este eh um documento de teste para validacao
do sistema de reconhecimento optico de caracteres.
Projeto de Estagio em Ciencia da Computacao."""
        
        # Adicionar texto à imagem
        linhas = texto.split('\n')
        y_pos = 40
        # Calcular altura da linha usando textbbox (compatível com PIL 10+)
        bbox = fonte.getbbox("Ay")
        line_height = (bbox[3] - bbox[1]) + 12 if bbox else 48
        for linha in linhas:
            d.text((40, y_pos), linha, fill='black', font=fonte)
            y_pos += line_height
        
        # Salvar imagem em PNG com DPI para melhor qualidade
        caminho_salvar = os.path.join(imagens_dir, "documento_teste.png")
        img.save(caminho_salvar, 'PNG', dpi=(300, 300))
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar imagem teste: {e}")
        return False

def listar_imagens(imagens_dir):
    """
    Lista todas as imagens na pasta 'imagens'
    """
    extensoes = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    imagens = []
    
    try:
        for arquivo in os.listdir(imagens_dir):
            if any(arquivo.lower().endswith(ext) for ext in extensoes):
                imagens.append(arquivo)
    except Exception as e:
        print(f"❌ Erro ao listar imagens: {e}")
    
    return imagens

def extrair_texto_simples(caminho_imagem):
    """
    Versão simples sem pré-processamento (para testes rápidos)
    """
    try:
        imagem = Image.open(caminho_imagem)
        texto = pytesseract.image_to_string(imagem, lang='por')
        return texto.strip()
    except Exception as e:
        return f"Erro: {e}"