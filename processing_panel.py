"""
Painel de processamento: encapsula área de resultado e botões para processar imagens.

API:
  ProcessingPanel(parent, imagens_dir, resultados_dir, process_image_fn, listar_images_fn, gerenciador, get_selected_fn)

"""
import os
import threading
import customtkinter as ctk
from tkinter import scrolledtext, messagebox
try:
    from cdigo.theme import PALETA
except Exception:
    from theme import PALETA


class ProcessingPanel(ctk.CTkFrame):
    def __init__(self, parent, imagens_dir, resultados_dir, process_image_fn, listar_images_fn, gerenciador, get_selected_fn, **kwargs):
        super().__init__(parent, **kwargs)
        self.imagens_dir = imagens_dir
        self.resultados_dir = resultados_dir
        self.process_image_fn = process_image_fn
        self.listar_images_fn = listar_images_fn
        self.gerenciador = gerenciador
        self.get_selected_fn = get_selected_fn
        self.parent = parent

        title_right = ctk.CTkLabel(self, text="✅ Resultado da Extração", font=("Segoe UI", 14, "bold"), text_color=PALETA["accent"])
        title_right.pack(anchor="w", pady=(0, 10))

        self.texto_resultado = scrolledtext.ScrolledText(self, font=("Courier New", 10), bg=PALETA["fundo_escuro"], fg=PALETA["sucesso"], insertbackground=PALETA["accent"])
        self.texto_resultado.pack(fill="both", expand=True, pady=(0, 10))

        process_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        process_btn_frame.pack(fill="x")

        ctk.CTkButton(process_btn_frame, text="▶️ Processar Selecionadas", font=("Segoe UI", 11, "bold"), fg_color=PALETA["botao_primario"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], command=self.process_selected, height=40).pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(process_btn_frame, text="⚡ Processar Tudo", font=("Segoe UI", 11, "bold"), fg_color=PALETA["botao_primario"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], command=self.process_all, height=40).pack(side="left", padx=5, fill="x", expand=True)

    def _save_text(self, imagem, texto):
        nome_salvar = imagem.split('.')[0] + "_texto.txt"
        caminho_salvar = os.path.join(self.resultados_dir, nome_salvar)
        try:
            with open(caminho_salvar, "w", encoding="utf-8") as f:
                f.write(texto)
        except Exception:
            pass

    def _append(self, txt):
        try:
            self.texto_resultado.insert("end", txt)
            self.texto_resultado.see("end")
            try:
                self.parent.update()
            except Exception:
                pass
        except Exception:
            pass

    def process_selected(self):
        selected = set()
        try:
            selected = set(self.get_selected_fn() or [])
        except Exception:
            selected = set()

        if not selected:
            messagebox.showwarning("Aviso", "Nenhuma imagem selecionada!")
            return

        # Run synchronously but keep UI responsive
        processadas = 0
        erros = 0
        self.texto_resultado.delete("1.0", "end")
        self._append(f"⏳ Processando {len(selected)} imagem(ns)...\n\n")

        for imagem in sorted(selected):
            self._append(f"🔄 {imagem}...\n")
            try:
                resultado = self.process_image_fn(imagem, self.imagens_dir)
                if resultado:
                    self._save_text(imagem, resultado)
                    try:
                        self.gerenciador.adicionar_documento(imagem, "genérico")
                    except Exception:
                        pass
                    self._append("✅ OK\n\n")
                    processadas += 1
                else:
                    self._append("❌ FALHA\n\n")
                    erros += 1
            except Exception as e:
                self._append(f"❌ ERRO: {e}\n\n")
                erros += 1

        self._append("\n" + '='*50 + "\n")
        self._append(f"📊 RESUMO: {processadas} processadas, {erros} erros\n")
        messagebox.showinfo("Sucesso", f"✅ {processadas} imagem(ns) processada(s)!")

    def process_all(self):
        imagens = []
        try:
            imagens = list(self.listar_images_fn(self.imagens_dir) or [])
        except Exception:
            imagens = []

        if not imagens:
            messagebox.showwarning("Aviso", "Nenhuma imagem encontrada!")
            return

        self.texto_resultado.delete("1.0", "end")
        processadas = 0
        erros = 0
        for img in imagens:
            self._append(f"🔄 {img}...\n")
            try:
                resultado = self.process_image_fn(img, self.imagens_dir)
                if resultado:
                    self._save_text(img, resultado)
                    try:
                        self.gerenciador.adicionar_documento(img, "genérico")
                    except Exception:
                        pass
                    self._append("✅ OK\n")
                    processadas += 1
                else:
                    self._append("❌ FALHA\n")
                    erros += 1
            except Exception as e:
                self._append(f"❌ ERRO: {e}\n")
                erros += 1

        self._append("\n" + '='*50 + "\n")
        self._append(f"📊 RESUMO: {processadas} processadas, {erros} erros\n")
        messagebox.showinfo("Sucesso", "⚡ Processamento concluído!")

    def set_dirs(self, imagens_dir=None, resultados_dir=None):
        """Atualiza os diretórios usados pelo painel."""
        if imagens_dir:
            self.imagens_dir = imagens_dir
        if resultados_dir:
            self.resultados_dir = resultados_dir

    def update_gerenciador(self, gerenciador):
        """Substitui o gerenciador de histórico usado."""
        self.gerenciador = gerenciador
