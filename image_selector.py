"""
Image selector widget: encapsula a lista de imagens, seleção e botões de ação.

Classe principal: ImageSelector(parent, imagens_dir, on_select_change=None)
"""
import os
import subprocess
import sys
import customtkinter as ctk
from tkinter import messagebox
from ocr_funcoes import listar_imagens
try:
    from cdigo.theme import PALETA
except Exception:
    from theme import PALETA


class ImageSelector(ctk.CTkFrame):
    def __init__(self, parent, imagens_dir, on_select_change=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.imagens_dir = imagens_dir
        self.on_select_change = on_select_change
        self.imagens_selecionadas = set()
        self.imagens_lista = []

        # Header with count label
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))
        self.label_title = ctk.CTkLabel(header, text="📸 Imagens Disponíveis", font=("Segoe UI", 14, "bold"), text_color=PALETA["accent"])
        self.label_title.pack(side="left", anchor="w")
        self.label_count = ctk.CTkLabel(header, text="(0 selecionadas)", font=("Segoe UI", 10), text_color=PALETA["texto_secundario"])
        self.label_count.pack(side="right", anchor="e")

        # Container list
        self.list_frame = ctk.CTkFrame(self, fg_color=PALETA["fundo_escuro"], corner_radius=8)
        self.list_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Canvas + scrollbar
        self.canvas = ctk.CTkCanvas(self.list_frame, bg=PALETA["fundo_escuro"], highlightthickness=0, height=350)
        self.scrollbar = ctk.CTkScrollbar(self.list_frame, command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color=PALETA["fundo_escuro"])

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(6, 0))

        ctk.CTkButton(btn_frame, text="🔄 Atualizar", font=("Segoe UI", 11, "bold"), fg_color=PALETA["botao_primario"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], command=self.refresh, height=40).pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="📁 Procurar", font=("Segoe UI", 11, "bold"), fg_color=PALETA["botao_primario"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], command=self.open_folder, height=40).pack(side="left", padx=5, fill="x", expand=True)

        select_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        select_btn_frame.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(select_btn_frame, text="✓ Selecionar Tudo", font=("Segoe UI", 10, "bold"), fg_color=PALETA["sucesso"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], command=self.select_all, height=35).pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(select_btn_frame, text="✗ Limpar Seleção", font=("Segoe UI", 10, "bold"), fg_color=PALETA["erro"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], command=self.clear_selection, height=35).pack(side="left", padx=5, fill="x", expand=True)

        # Initial load
        self.refresh()

    def refresh(self):
        # Clear
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        self.imagens_lista = listar_imagens(self.imagens_dir)
        if not self.imagens_lista:
            label = ctk.CTkLabel(self.scrollable_frame, text="📭 Nenhuma imagem encontrada", font=("Segoe UI", 12), text_color=PALETA["texto_secundario"]) 
            label.pack(pady=20)
            self.imagens_selecionadas.clear()
            self._notify_change()
            self._update_count()
            return

        for img in self.imagens_lista:
            self._create_item(img)

        self._update_count()

    def _create_item(self, imagem):
        item_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=PALETA["fundo_escuro"], corner_radius=6)
        item_frame.pack(fill="x", padx=5, pady=5)
        selecionada = imagem in self.imagens_selecionadas

        def toggle(img=imagem, frame=item_frame, btn_ref=None):
            if img in self.imagens_selecionadas:
                self.imagens_selecionadas.remove(img)
                frame.configure(fg_color=PALETA["fundo_escuro"])
                btn_ref.configure(text=f"☐ {img}")
            else:
                self.imagens_selecionadas.add(img)
                frame.configure(fg_color="#4a5568")
                btn_ref.configure(text=f"☑ {img}")
            self._update_count()
            self._notify_change()

        btn = ctk.CTkButton(item_frame, text=f"{'☑' if selecionada else '☐'} {imagem}", font=("Segoe UI", 11), fg_color="transparent", hover_color=PALETA["fundo_claro"], text_color=PALETA["texto_principal"], command=lambda i=imagem, f=item_frame, b=None: None, anchor="w", height=40)
        # we need to set the command after we have the btn reference
        btn.configure(command=lambda i=imagem, f=item_frame, b=btn: toggle(i, f, b))
        btn.pack(fill="both", expand=True, padx=10, pady=8)

        if selecionada:
            item_frame.configure(fg_color="#4a5568")

    def select_all(self):
        self.imagens_selecionadas = set(self.imagens_lista)
        self.refresh()
        self._notify_change()

    def clear_selection(self):
        self.imagens_selecionadas.clear()
        self.refresh()
        self._notify_change()

    def get_selected(self):
        return set(self.imagens_selecionadas)

    def open_folder(self):
        try:
            if sys.platform == "win32":
                subprocess.Popen(f'explorer "{self.imagens_dir}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.imagens_dir])
            else:
                subprocess.Popen(["xdg-open", self.imagens_dir])
            # refresh after brief delay
            self.after(800, self.refresh)
            messagebox.showinfo("Pasta Aberta", f"📁 Pasta aberta:\n{self.imagens_dir}\n\nColoque suas imagens lá e o programa detectará automaticamente!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir pasta: {str(e)}")

    def _update_count(self):
        qtd = len(self.imagens_selecionadas)
        self.label_count.configure(text=f"({qtd} selecionada{'s' if qtd != 1 else ''})")

    def _notify_change(self):
        if callable(self.on_select_change):
            try:
                self.on_select_change(set(self.imagens_selecionadas))
            except Exception:
                pass
