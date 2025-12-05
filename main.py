# main.py - Arquivo principal do sistema OCR
import pytesseract
from ocr_funcoes import processar_imagem, criar_imagem_teste, listar_imagens
import os
import csv
from datetime import datetime

# Configurar Tesseract (ajuste se necessário)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configurar TESSDATA_PREFIX para dados de idioma
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'


# ==================== GERENCIAMENTO DE HISTÓRICO ====================

try:
    from cdigo.history import GerenciadorDocumentos, exportar_para_csv, gerar_relatorio_estatisticas, menu_avancado
except Exception:
    # Fallback when running modules from the cdigo folder directly
    from history import GerenciadorDocumentos, exportar_para_csv, gerar_relatorio_estatisticas, menu_avancado


def gerar_relatorio_estatisticas(gerenciador):
    """Gera relatório completo do sistema"""
    documentos = gerenciador.buscar_documentos()
    
    print("\n" + "="*60)
    print("           RELATÓRIO DO SISTEMA OCR")
    print("="*60)
    print(f"Total de documentos processados: {len(documentos)}")
    
    if len(documentos) == 0:
        print("❌ Nenhum documento processado ainda.")
        return
    
    # Estatísticas por tipo
    tipos = {}
    for doc in documentos:
        if len(doc) > 2:
            tipo = doc[2]  # tipo_documento
            tipos[tipo] = tipos.get(tipo, 0) + 1
    
    print("\n📊 Documentos por tipo:")
    for tipo, quantidade in tipos.items():
        print(f"   {tipo}: {quantidade}")
    
    # Precisão média
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
        print(f"\n🎯 Precisão média: {sum(precisoes)/len(precisoes):.2f}%")
    
    # Últimos processamentos
    print(f"\n🕒 Último processamento: {documentos[-1][3] if len(documentos) > 0 and len(documentos[-1]) > 3 else 'N/A'}")


def menu_avancado(gerenciador):
    """Menu com funcionalidades avançadas"""
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
            gerar_relatorio_estatisticas(gerenciador)
            input("\nPressione Enter para continuar...")
        
        elif opcao == "2":
            tipo = input("Digite o tipo de documento: ")
            documentos = gerenciador.buscar_documentos(tipo)
            if documentos:
                print(f"\n📄 Documentos do tipo '{tipo}':")
                for doc in documentos:
                    if len(doc) > 3:
                        print(f"   - {doc[1]} (Processado em: {doc[3]})")
            else:
                print(f"❌ Nenhum documento do tipo '{tipo}' encontrado.")
            input("\nPressione Enter para continuar...")
        
        elif opcao == "3":
            exportar_para_csv(gerenciador)
            input("\nPressione Enter para continuar...")
        
        elif opcao == "4":
            print("↩️  Voltando ao menu principal...")
            break
        
        else:
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")


def exportar_para_csv(gerenciador):
    """Exporta dados para CSV"""
    documentos = gerenciador.buscar_documentos()
    
    if len(documentos) == 0:
        print("❌ Nenhum documento para exportar.")
        return
    
    # Usar a pasta pai do histórico (resultados/)
    pasta_resultados = os.path.dirname(gerenciador.arquivo_historico)
    arquivo_export = os.path.join(pasta_resultados, "exportacao_documentos.csv")
    
    try:
        with open(arquivo_export, 'w', newline='', encoding='utf-8') as arquivo:
            writer = csv.writer(arquivo)
            writer.writerow(['ID', 'Arquivo', 'Tipo', 'Data Processamento', 'Precisão'])
            for doc in documentos:
                writer.writerow(doc)
        print(f"✅ Dados exportados para: {arquivo_export}")
        print(f"📍 Caminho completo: {os.path.abspath(arquivo_export)}")
    except Exception as e:
        print(f"❌ Erro ao exportar: {e}")
        import traceback
        traceback.print_exc()


def menu_principal():
    print("=" * 50)
    print("       SISTEMA OCR - PROCESSAMENTO DE DOCUMENTOS")
    print("=" * 50)
    print("1 - Processar uma imagem específica")
    print("2 - Processar todas as imagens da pasta")
    print("3 - Criar imagem de teste")
    print("4 - Listar imagens disponíveis")
    print("6 - Menu avançado")
    print("5 - Sair")
    print("=" * 50)

def main():
    # Definir caminhos relativos à raiz do projeto (um nível acima de cdigo/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    imagens_dir = os.path.join(project_root, "imagens")
    resultados_dir = os.path.join(project_root, "resultados", "textos_extraidos")
    
    # Garantir que os diretórios existem
    os.makedirs(imagens_dir, exist_ok=True)
    os.makedirs(resultados_dir, exist_ok=True)
    
    # Inicializar gerenciador de documentos
    gerenciador = GerenciadorDocumentos(resultados_dir)
    
    while True:
        menu_principal()
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            # Processar imagem específica
            nome_imagem = input("Digite o nome da imagem (ex: documento.jpg): ")
            print(f"🔍 Procurando em: {imagens_dir}")
            print(f"📁 Arquivos disponíveis: {listar_imagens(imagens_dir)}")
            resultado = processar_imagem(nome_imagem, imagens_dir)
            
            if resultado:
                print("\n✅ TEXTO EXTRAÍDO:")
                print("=" * 40)
                print(resultado)
                print("=" * 40)
                
                # Salvar resultado
                nome_salvar = nome_imagem.split('.')[0] + "_texto.txt"
                caminho_salvar = os.path.join(resultados_dir, nome_salvar)
                
                with open(caminho_salvar, "w", encoding="utf-8") as arquivo:
                    arquivo.write(resultado)
                print(f"📁 Resultado salvo em: {caminho_salvar}")
                
                # Registrar no histórico
                tipo = input("Digite o tipo de documento (ou Enter para pular): ") or "genérico"
                gerenciador.adicionar_documento(nome_imagem, tipo)
            else:
                print("❌ Nenhum texto foi extraído. Verifique se a imagem existe e é válida.")
        
        elif opcao == "2":
            # Processar todas as imagens
            imagens = listar_imagens(imagens_dir)
            if imagens:
                tipo = input("Digite o tipo de documento (ou Enter para 'genérico'): ") or "genérico"
                for imagem in imagens:
                    print(f"\n🔄 Processando: {imagem}")
                    resultado = processar_imagem(imagem, imagens_dir)
                    if resultado:
                        print(f"✅ Concluído: {imagem}")
                        
                        # Salvar resultado
                        nome_salvar = imagem.split('.')[0] + "_texto.txt"
                        caminho_salvar = os.path.join(resultados_dir, nome_salvar)
                        
                        with open(caminho_salvar, "w", encoding="utf-8") as arquivo:
                            arquivo.write(resultado)
                        print(f"📁 Resultado salvo em: {caminho_salvar}")
                        
                        # Registrar no histórico
                        gerenciador.adicionar_documento(imagem, tipo)
            else:
                print("❌ Nenhuma imagem encontrada na pasta 'imagens'")
        
        elif opcao == "3":
            # Criar imagem de teste
            criar_imagem_teste()
            print(f"✅ Imagem de teste criada: {os.path.join(imagens_dir, 'documento_teste.png')}")
        
        elif opcao == "4":
            # Listar imagens
            imagens = listar_imagens(imagens_dir)
            if imagens:
                print("\n📸 Imagens disponíveis:")
                for img in imagens:
                    print(f"  - {img}")
            else:
                print("❌ Nenhuma imagem na pasta 'imagens'")
        
        elif opcao == "6":
            # Menu avançado
            menu_avancado(gerenciador)
        
        elif opcao == "5":
            print("👋 Saindo do sistema...")
            break
        
        else:
            print("❌ Opção inválida!")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()