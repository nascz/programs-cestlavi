# processador_dados.py - Extração inteligente de informações
import re
from datetime import datetime

class ProcessadorDados:
    @staticmethod
    def extrair_cpf(texto):
        cpfs = re.findall(r'\d{3}\.\d{3}\.\d{3}-\d{2}', texto)
        return cpfs[0] if cpfs else None
    
    @staticmethod
    def extrair_rg(texto):
        rgs = re.findall(r'\d{2}\.\d{3}\.\d{3}-\d{1}', texto)
        return rgs[0] if rgs else None
    
    @staticmethod
    def extrair_datas(texto):
        datas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
        return datas
    
    @staticmethod
    def extrair_nomes(texto):
        # Padrão simples para nomes (pode ser melhorado)
        padrao_nome = r'[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+'
        nomes = re.findall(padrao_nome, texto)
        return nomes
    
    @staticmethod
    def estruturar_dados(texto):
        return {
            'cpf': ProcessadorDados.extrair_cpf(texto),
            'rg': ProcessadorDados.extrair_rg(texto),
            'datas': ProcessadorDados.extrair_datas(texto),
            'nomes': ProcessadorDados.extrair_nomes(texto),
            'texto_completo': texto
        }