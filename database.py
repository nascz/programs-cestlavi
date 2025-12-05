# database.py - Integração com banco de dados
import sqlite3
import datetime
import json

class GerenciadorBancoDados:
    def __init__(self, nome_banco="documentos_ocr.db"):
        self.nome_banco = nome_banco
        self.criar_tabela()
    
    def criar_tabela(self):
        conn = sqlite3.connect(self.nome_banco)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_arquivo TEXT NOT NULL,
                texto_extraido TEXT,
                dados_estruturados TEXT,
                data_processamento TIMESTAMP,
                precisao_ocr REAL,
                tipo_documento TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def salvar_documento(self, nome_arquivo, texto_extraido, dados_estruturados=None, precisao=0.0):
        conn = sqlite3.connect(self.nome_banco)
        cursor = conn.cursor()
        
        # Detectar tipo de documento automaticamente
        tipo_doc = self.detectar_tipo_documento(texto_extraido)
        
        cursor.execute('''
            INSERT INTO documentos 
            (nome_arquivo, texto_extraido, dados_estruturados, data_processamento, precisao_ocr, tipo_documento)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome_arquivo, texto_extraido, json.dumps(dados_estruturados), 
              datetime.datetime.now(), precisao, tipo_doc))
        
        conn.commit()
        conn.close()
    
    def detectar_tipo_documento(self, texto):
        texto = texto.upper()
        if 'CPF' in texto and 'RG' in texto:
            return 'Documento de Identificação'
        elif 'NOTA FISCAL' in texto:
            return 'Nota Fiscal'
        elif 'CONTRATO' in texto:
            return 'Contrato'
        else:
            return 'Documento Geral'
    
    def buscar_documentos(self, tipo=None):
        conn = sqlite3.connect(self.nome_banco)
        cursor = conn.cursor()
        
        if tipo:
            cursor.execute('SELECT * FROM documentos WHERE tipo_documento = ?', (tipo,))
        else:
            cursor.execute('SELECT * FROM documentos ORDER BY data_processamento DESC')
        
        resultados = cursor.fetchall()
        conn.close()
        return resultados

# Adicione isso ao seu main.py
from database import GerenciadorBancoDados

# No início do main()
db = GerenciadorBancoDados()