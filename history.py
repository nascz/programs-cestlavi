"""
Módulo para gerenciamento de histórico (anteriormente em main.py)
Fornece: GerenciadorDocumentos, exportar_para_csv, gerar_relatorio_estatisticas, menu_avancado
"""
import os
import csv
from datetime import datetime


class GerenciadorDocumentos:
    """Gerencia o histórico de documentos processados"""
    def __init__(self, resultados_dir):
        self.resultados_dir = resultados_dir
        self.arquivo_historico = os.path.join(resultados_dir, "historico_documentos.csv")
        self._criar_arquivo_historico()

    def _criar_arquivo_historico(self):
        if not os.path.exists(self.arquivo_historico):
            os.makedirs(os.path.dirname(self.arquivo_historico), exist_ok=True)
            with open(self.arquivo_historico, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Arquivo', 'Tipo', 'Data Processamento', 'Precisão'])

    def adicionar_documento(self, nome_arquivo, tipo_documento="genérico", precisao=0):
        try:
            with open(self.arquivo_historico, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                doc_id = len(self.buscar_documentos()) + 1
                data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                writer.writerow([doc_id, nome_arquivo, tipo_documento, data, precisao])
        except Exception as e:
            print(f"❌ Erro ao salvar histórico: {e}")

    def buscar_documentos(self, tipo=None):
        documentos = []
        try:
            if not os.path.exists(self.arquivo_historico):
                return documentos
            with open(self.arquivo_historico, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Pular cabeçalho
                for row in reader:
                    if tipo is None or (len(row) > 2 and row[2] == tipo):
                        documentos.append(row)
        except Exception as e:
            print(f"❌ Erro ao ler histórico: {e}")
        return documentos


def exportar_para_csv(gerenciador, dest_dir: str = None):
    """Exporta dados do gerenciador para CSV.

    Se `dest_dir` for None, usa a pasta do histórico (resultados). Caso contrário, escreve em `dest_dir/exportacao_documentos.csv`.
    Retorna o caminho do arquivo exportado ou None em caso de erro.
    """
    documentos = gerenciador.buscar_documentos()
    if len(documentos) == 0:
        print("❌ Nenhum documento para exportar.")
        return None

    if dest_dir:
        pasta_resultados = dest_dir
    else:
        pasta_resultados = os.path.dirname(gerenciador.arquivo_historico)

    os.makedirs(pasta_resultados, exist_ok=True)
    arquivo_export = os.path.join(pasta_resultados, "exportacao_documentos.csv")
    try:
        with open(arquivo_export, 'w', newline='', encoding='utf-8') as arquivo:
            writer = csv.writer(arquivo)
            writer.writerow(['ID', 'Arquivo', 'Tipo', 'Data Processamento', 'Precisão'])
            for doc in documentos:
                writer.writerow(doc)
        print(f"✅ Dados exportados para: {arquivo_export}")
        return arquivo_export
    except Exception as e:
        print(f"❌ Erro ao exportar: {e}")
        return None


def gerar_relatorio_estatisticas(gerenciador):
    documentos = gerenciador.buscar_documentos()
    relatorio = []
    relatorio.append('='*60)
    relatorio.append('RELATÓRIO DO SISTEMA OCR')
    relatorio.append('='*60)
    relatorio.append(f"Total de documentos processados: {len(documentos)}")

    if len(documentos) == 0:
        relatorio.append('Nenhum documento processado ainda.')
        return '\n'.join(relatorio)

    tipos = {}
    for doc in documentos:
        if len(doc) > 2:
            tipo = doc[2]
            tipos[tipo] = tipos.get(tipo, 0) + 1

    relatorio.append('\nDocumentos por tipo:')
    for tipo, quantidade in tipos.items():
        relatorio.append(f"   {tipo}: {quantidade}")

    precisoes = []
    for doc in documentos:
        if len(doc) > 4:
            try:
                prec = float(doc[4])
                if prec > 0:
                    precisoes.append(prec)
            except:
                pass

    if precisoes:
        relatorio.append(f"\nPrecisão média: {sum(precisoes)/len(precisoes):.2f}%")

    relatorio.append(f"\nÚltimo processamento: {documentos[-1][3] if len(documentos) > 0 and len(documentos[-1]) > 3 else 'N/A'}")
    return '\n'.join(relatorio)


def menu_avancado(gerenciador):
    while True:
        print("\n" + "="*50)
        print("          MENU AVANÇADO - SISTEMA OCR")
        print("="*50)
        print("1 - Ver relatório estatístico")
        print("2 - Buscar documentos por tipo")
        print("3 - Exportar dados para CSV")
        print("4 - Voltar ao menu principal")
        print("="*50)
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            print(gerar_relatorio_estatisticas(gerenciador))
            input("\nPressione Enter para continuar...")
        elif opcao == "2":
            tipo = input("Digite o tipo de documento: ")
            documentos = gerenciador.buscar_documentos(tipo)
            if documentos:
                print(f"\nDocumentos do tipo '{tipo}':")
                for doc in documentos:
                    if len(doc) > 3:
                        print(f"   - {doc[1]} (Processado em: {doc[3]})")
            else:
                print(f"Nenhum documento do tipo '{tipo}' encontrado.")
            input("\nPressione Enter para continuar...")
        elif opcao == "3":
            exportar_para_csv(gerenciador)
            input("\nPressione Enter para continuar...")
        elif opcao == "4":
            break
        else:
            print("Opção inválida!")
            input("\nPressione Enter para continuar...")
