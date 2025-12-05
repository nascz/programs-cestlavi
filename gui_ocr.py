import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import os
import threading
import sys
from datetime import datetime
from ocr_funcoes import processar_imagem, criar_imagem_teste, listar_imagens

try:
    from cdigo.config import load_config, save_config
    from cdigo.theme import PALETA, apply_customtkinter_theme
    from cdigo.history import GerenciadorDocumentos, exportar_para_csv
    from cdigo.image_selector import ImageSelector
    from cdigo.processing_panel import ProcessingPanel
    from cdigo.results_viewer import ResultsViewer
except ImportError:
    from config import load_config, save_config
    from theme import PALETA, apply_customtkinter_theme
    from history import GerenciadorDocumentos, exportar_para_csv
    from image_selector import ImageSelector
    from processing_panel import ProcessingPanel
    from results_viewer import ResultsViewer

apply_customtkinter_theme(ctk)


class OCRguiModerna:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Sistema OCR - Processamento de Documentos")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        
        self.imagens_dir, self.resultados_dir = self._resolve_paths()
        os.makedirs(self.imagens_dir, exist_ok=True)
        os.makedirs(self.resultados_dir, exist_ok=True)
        
        self.gerenciador = GerenciadorDocumentos(self.resultados_dir)
        self.imagens_selecionadas = set()
        self.imagens_lista = []
        self.criar_interface()
    
    def _resolve_paths(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exe_cwd = os.getcwd()
        
        cmd_imagens_dir = sys.argv[1] if len(sys.argv) > 1 else None
        if cmd_imagens_dir and not os.path.isabs(cmd_imagens_dir):
            cmd_imagens_dir = os.path.abspath(cmd_imagens_dir)
        
        candidatos_imagens = [cmd_imagens_dir, os.path.join(exe_cwd, "imagens"), os.path.join(project_root, "imagens")] if cmd_imagens_dir else [os.path.join(exe_cwd, "imagens"), os.path.join(project_root, "imagens")]
        chosen_imagens = next((c for c in candidatos_imagens if c and os.path.isdir(c)), os.path.join(exe_cwd, "imagens"))
        
        candidatos_resultados = [os.path.join(exe_cwd, "resultados", "textos_extraidos"), os.path.join(project_root, "resultados", "textos_extraidos")]
        chosen_resultados = next((c for c in candidatos_resultados if os.path.isdir(c)), os.path.join(exe_cwd, "resultados", "textos_extraidos"))
        
        cfg = load_config() or {}
        imagens_dir = os.path.abspath(cfg.get('imagens_dir') or chosen_imagens)
        resultados_dir = os.path.abspath(cfg.get('resultados_dir') or chosen_resultados)
        
        return imagens_dir, resultados_dir
    
    def criar_interface(self):
        """Cria a interface gráfica moderna"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color=PALETA["fundo_escuro"])
        self.main_frame.pack(fill="both", expand=True)
        
        # Cabeçalho com gradient
        header = ctk.CTkFrame(self.main_frame, height=100, fg_color=PALETA["header"], corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header,
            text="📄 SISTEMA OCR",
            font=("Segoe UI", 32, "bold"),
            text_color=PALETA["accent"]
        )
        title_label.pack(pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header,
            text="Processamento Inteligente de Documentos",
            font=("Segoe UI", 13),
            text_color=PALETA["texto_secundario"]
        )
        subtitle_label.pack()
        
        # Container com abas
        self.tab_container = ctk.CTkFrame(self.main_frame, fg_color=PALETA["fundo_escuro"])
        self.tab_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Criar abas
        self.criar_abas()
    
    def criar_abas(self):
        """Cria as abas da aplicação"""
        # Frame de botões das abas
        tab_buttons_frame = ctk.CTkFrame(self.tab_container, fg_color=PALETA["fundo_claro"], height=50)
        tab_buttons_frame.pack(fill="x", padx=0, pady=0)
        tab_buttons_frame.pack_propagate(False)
        
        self.aba_atual = "processar"
        
        # Botões das abas
        tabs_config = [
            ("🖼️ Processar", "processar"),
            ("✨ Criar Teste", "teste"),
            ("📊 Relatório", "relatorio"),
            ("📂 Resultados", "resultados"),
            ("📋 Histórico", "historico")
        ]
        
        for label, tab_name in tabs_config:
            btn = ctk.CTkButton(
                tab_buttons_frame,
                text=label,
                font=("Segoe UI", 12, "bold"),
                fg_color=PALETA["botao_primario"],
                hover_color=PALETA["botao_hover"],
                text_color=PALETA["texto_principal"],
                command=lambda t=tab_name: self.mudar_aba(t),
                height=45
            )
            btn.pack(side="left", padx=5, pady=5)
        
        # Frame para conteúdo das abas
        self.content_frame = ctk.CTkFrame(self.tab_container, fg_color=PALETA["fundo_claro"])
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=(10, 0))
        
        # Criar conteúdo das abas (inicialmente vazio)
        self.abas = {}
        self.mudar_aba("processar")
    
    def limpar_content(self):
        """Limpa o frame de conteúdo"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def mudar_aba(self, tab_name):
        """Muda para a aba especificada"""
        self.aba_atual = tab_name
        self.limpar_content()
        
        if tab_name == "processar":
            self.criar_aba_processar()
        elif tab_name == "teste":
            self.criar_aba_teste()
        elif tab_name == "relatorio":
            self.criar_aba_relatorio()
        elif tab_name == "resultados":
            self.criar_aba_resultados()
        elif tab_name == "historico":
            self.criar_aba_historico()
    
    def criar_aba_processar(self):
        """Aba para processar imagens"""
        # Divisão esquerda e direita
        left_frame = ctk.CTkFrame(self.content_frame, fg_color=PALETA["fundo_claro"])
        left_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        right_frame = ctk.CTkFrame(self.content_frame, fg_color=PALETA["fundo_claro"])
        right_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        
        # === LEFT SIDE === (delegado para ImageSelector)
        # Cabeçalho simples — o selector cria sua própria listagem e botões
        header_left = ctk.CTkFrame(left_frame, fg_color="transparent")
        header_left.pack(fill="x", pady=(0, 10))
        title_left = ctk.CTkLabel(header_left, text="📸 Imagens Disponíveis", font=("Segoe UI", 14, "bold"), text_color=PALETA["accent"])
        title_left.pack(side="left", anchor="w")
        self.label_selecionadas = ctk.CTkLabel(header_left, text="(0 selecionadas)", font=("Segoe UI", 10), text_color=PALETA["texto_secundario"])
        self.label_selecionadas.pack(side="right", anchor="e")

        try:
            from cdigo.image_selector import ImageSelector
        except Exception:
            from image_selector import ImageSelector

        try:
            from cdigo.processing_panel import ProcessingPanel
        except Exception:
            from processing_panel import ProcessingPanel

        try:
            from cdigo.results_viewer import ResultsViewer
        except Exception:
            from results_viewer import ResultsViewer

        # instanciar selector (ele empacota a lista e botões)
        self.selector = ImageSelector(left_frame, self.imagens_dir, on_select_change=self._on_select_change)
        self.selector.pack(fill="both", expand=True)
        
        # Paths display + controls (mostra onde os resultados serão salvos)
        paths_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        paths_frame.pack(fill="x", pady=(8, 6))

        self.label_path_images = ctk.CTkLabel(paths_frame, text=f"Imagens: {self.imagens_dir}", font=("Segoe UI", 9), text_color=PALETA["texto_secundario"]) 
        self.label_path_images.pack(side="left", anchor="w")
        ctk.CTkButton(paths_frame, text="Alterar Imagens", font=("Segoe UI", 9), fg_color=PALETA["botao_primario"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], command=self.choose_images_folder, height=28, width=140).pack(side="right", padx=4)

        paths_frame2 = ctk.CTkFrame(left_frame, fg_color="transparent")
        paths_frame2.pack(fill="x")
        self.label_path_results = ctk.CTkLabel(paths_frame2, text=f"Resultados: {self.resultados_dir}", font=("Segoe UI", 9), text_color=PALETA["texto_secundario"]) 
        self.label_path_results.pack(side="left", anchor="w")
        ctk.CTkButton(paths_frame2, text="Alterar Resultados", font=("Segoe UI", 9), fg_color=PALETA["botao_primario"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], command=self.choose_results_folder, height=28, width=140).pack(side="right", padx=4)
        
        # === RIGHT SIDE === (delegado ao ProcessingPanel)
        try:
            self.processing_panel = ProcessingPanel(right_frame, self.imagens_dir, self.resultados_dir, processar_imagem, listar_imagens, self.gerenciador, get_selected_fn=lambda: self.selector.get_selected())
            self.processing_panel.pack(fill="both", expand=True)
        except Exception:
            # Fallback: criar área de texto mínima
            title_right = ctk.CTkLabel(right_frame, text="✅ Resultado da Extração", font=("Segoe UI", 14, "bold"), text_color=PALETA["accent"])
            title_right.pack(anchor="w", pady=(0, 10))
            self.texto_resultado = scrolledtext.ScrolledText(right_frame, font=("Courier New", 10), bg=PALETA["fundo_escuro"], fg=PALETA["sucesso"], insertbackground=PALETA["accent"])
            self.texto_resultado.pack(fill="both", expand=True, pady=(0, 10))
        
        # Atualizar lista
        self.atualizar_lista_imagens()

    def choose_images_folder(self):
        """Permite ao usuário escolher a pasta de imagens e atualiza componentes."""
        try:
            pasta = filedialog.askdirectory(initialdir=self.imagens_dir, title="Selecione a pasta de imagens")
            if pasta:
                self.imagens_dir = os.path.abspath(pasta)
                os.makedirs(self.imagens_dir, exist_ok=True)
                # atualizar label
                self.label_path_images.configure(text=f"Imagens: {self.imagens_dir}")
                # atualizar selector
                if hasattr(self, 'selector') and self.selector is not None:
                    try:
                        self.selector.imagens_dir = self.imagens_dir
                        self.selector.refresh()
                    except Exception:
                        pass
                # atualizar processing panel
                if hasattr(self, 'processing_panel') and self.processing_panel is not None:
                    try:
                        self.processing_panel.set_dirs(imagens_dir=self.imagens_dir)
                    except Exception:
                        pass
                # salvar config
                try:
                    save_config({'imagens_dir': self.imagens_dir, 'resultados_dir': self.resultados_dir})
                except Exception:
                    pass
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar pasta de imagens: {e}")

    def choose_results_folder(self):
        """Permite ao usuário escolher a pasta de resultados e atualiza componentes."""
        try:
            pasta = filedialog.askdirectory(initialdir=self.resultados_dir, title="Selecione a pasta de resultados")
            if pasta:
                self.resultados_dir = os.path.abspath(pasta)
                os.makedirs(self.resultados_dir, exist_ok=True)
                # atualizar label
                self.label_path_results.configure(text=f"Resultados: {self.resultados_dir}")
                # atualizar gerenciador (recria o arquivo de histórico no novo local)
                try:
                    self.gerenciador = GerenciadorDocumentos(self.resultados_dir)
                except Exception:
                    pass
                # atualizar processing panel
                if hasattr(self, 'processing_panel') and self.processing_panel is not None:
                    try:
                        self.processing_panel.set_dirs(resultados_dir=self.resultados_dir)
                        self.processing_panel.update_gerenciador(self.gerenciador)
                    except Exception:
                        pass
                # atualizar histórico exibido
                try:
                    self.mostrar_historico()
                except Exception:
                    pass
                # salvar config
                try:
                    save_config({'imagens_dir': self.imagens_dir, 'resultados_dir': self.resultados_dir})
                except Exception:
                    pass
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar pasta de resultados: {e}")

    def _on_select_change(self, selected_set):
        """Callback do ImageSelector quando a seleção muda"""
        try:
            self.imagens_selecionadas = set(selected_set)
            qtd = len(self.imagens_selecionadas)
            self.label_selecionadas.configure(text=f"({qtd} selecionada{'s' if qtd != 1 else ''})")
        except Exception:
            pass
    
    def criar_aba_teste(self):
        """Aba para criar imagem de teste"""
        frame = ctk.CTkFrame(self.content_frame, fg_color=PALETA["fundo_claro"])
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Ícone grande
        icon_label = ctk.CTkLabel(frame, text="✨", font=("Arial", 80), text_color=PALETA["accent"])
        icon_label.pack(pady=20)
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="Criar Imagem de Teste",
            font=("Segoe UI", 20, "bold"),
            text_color=PALETA["texto_principal"]
        )
        title.pack(pady=10)
        
        # Descrição
        desc = ctk.CTkLabel(
            frame,
            text="Gera um documento fictício para testar o sistema OCR.\nA imagem será salva na pasta 'imagens/'",
            font=("Segoe UI", 12),
            text_color=PALETA["texto_secundario"]
        )
        desc.pack(pady=20)
        
        # Botão
        ctk.CTkButton(
            frame,
            text="✨ Criar Imagem de Teste",
            font=("Segoe UI", 14, "bold"),
            fg_color=PALETA["botao_primario"],
            hover_color=PALETA["botao_hover"],
            text_color=PALETA["texto_principal"],
            command=self.criar_teste,
            height=50,
            width=300
        ).pack(pady=30)

    def criar_aba_resultados(self):
        """Aba para visualizar resultados processados"""
        frame = ctk.CTkFrame(self.content_frame, fg_color=PALETA["fundo_claro"])
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        try:
            rv = ResultsViewer(frame, self.resultados_dir)
            rv.pack(fill="both", expand=True)
            self.results_viewer = rv
        except Exception as e:
            # fallback display
            ctk.CTkLabel(frame, text=f"Erro ao carregar ResultsViewer: {e}", text_color=PALETA["erro"]).pack(padx=10, pady=10)
    
    def criar_aba_relatorio(self):
        """Aba para exibir relatório"""
        # Botões no topo
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="📊 Gerar Relatório",
            font=("Segoe UI", 11, "bold"),
            fg_color=PALETA["botao_primario"],
            hover_color=PALETA["botao_hover"],
            text_color=PALETA["texto_principal"],
            command=self.gerar_relatorio,
            height=40
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Exportar CSV",
            font=("Segoe UI", 11, "bold"),
            fg_color=PALETA["botao_primario"],
            hover_color=PALETA["botao_hover"],
            text_color=PALETA["texto_principal"],
            command=self.exportar_csv,
            height=40
        ).pack(side="left", padx=5)

        # Mostrar caminho padrão de exportação e permitir escolher pasta
        export_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        export_frame.pack(fill="x", padx=15, pady=(6, 8))
        default_export_path = os.path.join(self.resultados_dir, 'exportacao_documentos.csv')
        self.label_export_path = ctk.CTkLabel(export_frame, text=f"CSV padrão: {default_export_path}", font=("Segoe UI", 9), text_color=PALETA["texto_secundario"]) 
        self.label_export_path.pack(side="left", anchor="w")
        ctk.CTkButton(export_frame, text="Exportar Para...", font=("Segoe UI", 10), fg_color=PALETA["botao_primario"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], command=self.exportar_para_destino, height=28, width=140).pack(side="right")
        
        # Área de texto
        self.texto_relatorio = scrolledtext.ScrolledText(self.content_frame, font=("Courier New", 10), bg=PALETA["fundo_escuro"], fg=PALETA["sucesso"], insertbackground=PALETA["accent"])
        self.texto_relatorio.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    def criar_aba_historico(self):
        """Aba para exibir histórico"""
        # Filtro no topo
        filter_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(filter_frame, text="Filtrar por tipo:", font=("Segoe UI", 11), text_color=PALETA["texto_secundario"]).pack(side="left", padx=5)
        
        self.entrada_tipo = ctk.CTkEntry(filter_frame, font=("Segoe UI", 11), width=200, placeholder_text="Digite o tipo...", text_color=PALETA["texto_principal"], fg_color=PALETA["fundo_escuro"])
        self.entrada_tipo.pack(side="left", padx=5)
        
        ctk.CTkButton(
            filter_frame,
            text="🔍 Filtrar",
            font=("Segoe UI", 11, "bold"),
            fg_color=PALETA["botao_primario"],
            hover_color=PALETA["botao_hover"],
            text_color=PALETA["texto_principal"],
            command=self.filtrar_historico,
            height=35,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            filter_frame,
            text="📋 Mostrar Tudo",
            font=("Segoe UI", 11, "bold"),
            fg_color=PALETA["botao_primario"],
            hover_color=PALETA["botao_hover"],
            text_color=PALETA["texto_principal"],
            command=self.mostrar_historico,
            height=35,
            width=120
        ).pack(side="left", padx=5)
        
        # Tabela de histórico
        self.texto_historico = scrolledtext.ScrolledText(self.content_frame, font=("Courier New", 10), bg=PALETA["fundo_escuro"], fg=PALETA["sucesso"], insertbackground=PALETA["accent"])
        self.texto_historico.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.mostrar_historico()
    
    def atualizar_lista_imagens(self):
        """Atualiza a lista através do selector"""
        try:
            if hasattr(self, 'selector') and self.selector is not None:
                self.selector.refresh()
                # atualizar contador também
                qtd = len(self.selector.get_selected())
                self.label_selecionadas.configure(text=f"({qtd} selecionada{'s' if qtd != 1 else ''})")
        except Exception:
            pass
    
    def criar_item_imagem(self, parent, idx, imagem):
        """Cria um item clicável para cada imagem"""
        # agora delegado para ImageSelector; mantido por compatibilidade
        return
    
    def abrir_pasta_imagens(self):
        """Abre a pasta de imagens no explorador"""
        # Delegado ao selector (mantenha por compatibilidade)
        try:
            if hasattr(self, 'selector') and self.selector is not None:
                self.selector.open_folder()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir pasta: {str(e)}")
    
    def selecionar_tudo(self):
        if hasattr(self, 'selector') and self.selector is not None:
            self.selector.select_all()
    
    def limpar_selecao(self):
        if hasattr(self, 'selector') and self.selector is not None:
            self.selector.clear_selection()
    
    def atualizar_contador_selecao(self):
        """Atualiza o contador de seleção"""
        if hasattr(self, 'selector') and self.selector is not None:
            qtd = len(self.selector.get_selected())
        else:
            qtd = len(getattr(self, 'imagens_selecionadas', []))
        self.label_selecionadas.configure(text=f"({qtd} selecionada{'s' if qtd != 1 else ''})")
    
    def processar_selecionada(self):
        """Processa as imagens selecionadas"""
        # Delegar para processing_panel quando disponível
        try:
            if hasattr(self, 'processing_panel') and self.processing_panel is not None:
                return self.processing_panel.process_selected()
        except Exception:
            pass

        # Fallback: antigo comportamento
        selecionadas = set()
        if hasattr(self, 'selector') and self.selector is not None:
            selecionadas = self.selector.get_selected()
        else:
            selecionadas = getattr(self, 'imagens_selecionadas', set())

        if not selecionadas:
            messagebox.showwarning("Aviso", "Nenhuma imagem selecionada!")
            return

        # minimal fallback processing (kept for compatibility)
        try:
            self.texto_resultado.delete("1.0", "end")
            self.texto_resultado.insert("end", f"⏳ Processando {len(selecionadas)} imagem(ns)...\n\n")
            self.root.update()
            for imagem in sorted(selecionadas):
                self.texto_resultado.insert("end", f"🔄 {imagem}...\n")
                self.root.update()
                resultado = processar_imagem(imagem, self.imagens_dir)
                if resultado:
                    nome_salvar = imagem.split('.')[0] + "_texto.txt"
                    caminho_salvar = os.path.join(self.resultados_dir, nome_salvar)
                    with open(caminho_salvar, "w", encoding="utf-8") as f:
                        f.write(resultado)
                    self.gerenciador.adicionar_documento(imagem, "genérico")
                    self.texto_resultado.insert("end", f"✅ OK\n\n")
                else:
                    self.texto_resultado.insert("end", f"❌ FALHA\n\n")
            self.mostrar_historico()
            messagebox.showinfo("Sucesso", "Processamento concluído")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def processar_todas(self):
        """Processa todas as imagens"""
        # Preferir o panel
        try:
            if hasattr(self, 'processing_panel') and self.processing_panel is not None:
                return self.processing_panel.process_all()
        except Exception:
            pass

        # Fallback (compat)
        try:
            imagens = listar_imagens(self.imagens_dir)
            if not imagens:
                messagebox.showwarning("Aviso", "Nenhuma imagem encontrada!")
                return
            self.texto_resultado.delete("1.0", "end")
            for img in imagens:
                self.texto_resultado.insert("end", f"🔄 {img}...\n")
                self.root.update()
                resultado = processar_imagem(img, self.imagens_dir)
                if resultado:
                    nome_salvar = img.split('.')[0] + "_texto.txt"
                    caminho_salvar = os.path.join(self.resultados_dir, nome_salvar)
                    with open(caminho_salvar, "w", encoding="utf-8") as f:
                        f.write(resultado)
                    self.gerenciador.adicionar_documento(img, "genérico")
                    self.texto_resultado.insert("end", f"✅ OK\n")
                else:
                    self.texto_resultado.insert("end", f"❌ FALHA\n")
            self.mostrar_historico()
            messagebox.showinfo("Sucesso", "⚡ Processamento concluído!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def criar_teste(self):
        """Cria imagem de teste"""
        try:
            criar_imagem_teste()
            self.atualizar_lista_imagens()
            messagebox.showinfo("Sucesso", "✨ Imagem de teste criada!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def gerar_relatorio(self):
        """Gera relatório"""
        try:
            self.texto_relatorio.delete("1.0", "end")
            
            documentos = self.gerenciador.buscar_documentos()
            
            relatorio = "="*60 + "\n"
            relatorio += "RELATÓRIO DO SISTEMA OCR\n"
            relatorio += "="*60 + "\n\n"
            relatorio += f"Total de documentos: {len(documentos)}\n"
            
            if len(documentos) == 0:
                relatorio += "\n❌ Nenhum documento processado.\n"
            else:
                tipos = {}
                for doc in documentos:
                    if len(doc) > 2:
                        tipo = doc[2]
                        tipos[tipo] = tipos.get(tipo, 0) + 1
                
                relatorio += "\n📊 POR TIPO:\n"
                for tipo, qtd in tipos.items():
                    relatorio += f"   {tipo}: {qtd}\n"
                
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
                    relatorio += f"\n🎯 Precisão média: {sum(precisoes)/len(precisoes):.2f}%\n"
                
                relatorio += f"\n🕒 Último: {documentos[-1][3] if len(documentos[-1]) > 3 else 'N/A'}\n"
            
            self.texto_relatorio.insert("1.0", relatorio)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def exportar_csv(self):
        """Exporta para CSV"""
        try:
            path = exportar_para_csv(self.gerenciador)
            if path:
                messagebox.showinfo("Sucesso", f"💾 CSV exportado: {path}")
            else:
                messagebox.showwarning("Aviso", "Nenhum documento para exportar.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    def exportar_para_destino(self):
        """Exporta o CSV para uma pasta escolhida pelo usuário."""
        try:
            pasta = filedialog.askdirectory(initialdir=self.resultados_dir, title="Escolha a pasta para exportar o CSV")
            if not pasta:
                return
            caminho = exportar_para_csv(self.gerenciador, dest_dir=pasta)
            if caminho:
                messagebox.showinfo("Sucesso", f"CSV exportado para: {caminho}")
                # atualizar label de caminho
                try:
                    self.label_export_path.configure(text=f"CSV padrão: {os.path.join(self.resultados_dir, 'exportacao_documentos.csv')}")
                except Exception:
                    pass
            else:
                messagebox.showerror("Erro", "Falha ao exportar CSV.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")
    
    def mostrar_historico(self):
        """Mostra histórico"""
        if not hasattr(self, 'texto_historico'):
            return
        
        self.texto_historico.delete("1.0", "end")
        
        documentos = self.gerenciador.buscar_documentos()
        
        if not documentos:
            self.texto_historico.insert("end", "📭 Nenhum documento no histórico\n")
            return
        
        # Cabeçalho
        header = f"{'ID':<5} {'Arquivo':<30} {'Tipo':<15} {'Data':<20}\n"
        header += "-" * 70 + "\n"
        self.texto_historico.insert("end", header)
        
        for doc in documentos:
            if len(doc) >= 4:
                line = f"{doc[0]:<5} {doc[1]:<30} {doc[2]:<15} {doc[3]:<20}\n"
                self.texto_historico.insert("end", line)
    
    def filtrar_historico(self):
        """Filtra histórico"""
        tipo = self.entrada_tipo.get().strip()
        
        if not tipo:
            self.mostrar_historico()
            return
        
        if not hasattr(self, 'texto_historico'):
            return
        
        self.texto_historico.delete("1.0", "end")
        
        documentos = self.gerenciador.buscar_documentos(tipo)
        
        if not documentos:
            self.texto_historico.insert("end", f"❌ Nenhum documento do tipo '{tipo}'\n")
            return
        
        header = f"{'ID':<5} {'Arquivo':<30} {'Tipo':<15} {'Data':<20}\n"
        header += "-" * 70 + "\n"
        self.texto_historico.insert("end", header)
        
        for doc in documentos:
            if len(doc) >= 4:
                line = f"{doc[0]:<5} {doc[1]:<30} {doc[2]:<15} {doc[3]:<20}\n"
                self.texto_historico.insert("end", line)


if __name__ == "__main__":
    root = ctk.CTk()
    app = OCRguiModerna(root)
    root.mainloop()

