import os
import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, messagebox
try:
    from cdigo.theme import PALETA
except Exception:
    from theme import PALETA


class ResultsViewer(ctk.CTkFrame):
    def __init__(self, parent, resultados_dir, **kwargs):
        super().__init__(parent, **kwargs)
        self.resultados_dir = resultados_dir

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(top, text="📂 Resultados Processados", font=("Segoe UI", 14, "bold"), text_color=PALETA["accent"]).pack(side="left")
        ctk.CTkButton(top, text="🔄 Atualizar", font=("Segoe UI", 10), command=self.refresh, fg_color=PALETA["botao_primario"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], height=30).pack(side="right")

        body = ctk.CTkFrame(self, fg_color=PALETA["fundo_claro"])
        body.pack(fill="both", expand=True)

        left = ctk.CTkFrame(body, fg_color=PALETA["fundo_claro"])
        left.pack(side="left", fill="y", padx=(10, 5), pady=10)

        right = ctk.CTkFrame(body, fg_color=PALETA["fundo_claro"])
        right.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        tk_container = tk.Frame(left, bg=PALETA.get("fundo_escuro", "#222"))
        tk_container.pack(fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(tk_container, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(
            tk_container,
            selectmode='extended',
            yscrollcommand=self.scrollbar.set,
            bg=PALETA.get("fundo_escuro", "#222"),
            fg=PALETA.get("texto_principal", "#fff"),
            activestyle='none',
            highlightthickness=0,
            bd=0,
            exportselection=False,
        )
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind('<<ListboxSelect>>', lambda e: self.on_select())

        self.preview = scrolledtext.ScrolledText(right, font=("Courier New", 10), bg=PALETA["fundo_escuro"], fg=PALETA["texto_principal"], insertbackground=PALETA["accent"])
        self.preview.pack(fill="both", expand=True)

        btns = ctk.CTkFrame(right, fg_color="transparent")
        btns.pack(fill="x", pady=(8, 0))
        ctk.CTkButton(btns, text="Abrir Pasta", command=self.open_folder, fg_color=PALETA["botao_primario"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], height=36).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Remover Selecionados", command=self.remove_selected, fg_color=PALETA["erro"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], height=36).pack(side="right", padx=6)
        ctk.CTkButton(btns, text="Pré-visualizar", command=self.preview_selected, fg_color=PALETA["botao_secundario"], hover_color=PALETA["botao_hover"], text_color=PALETA["texto_principal"], height=36).pack(side="right", padx=6)

        self.refresh()

    def _list_results(self):
        try:
            files = []
            for f in os.listdir(self.resultados_dir):
                if f.lower().endswith('.txt'):
                    files.append(f)
            files.sort()
            return files
        except Exception:
            return []

    def refresh(self):
        # Clear native listbox
        self.listbox.delete(0, tk.END)
        files = self._list_results()
        if not files:
            self.listbox.insert(tk.END, "(Nenhum resultado encontrado)")
            self.listbox.config(state=tk.DISABLED)
            self.preview.delete('1.0', 'end')
            return

        self.listbox.config(state=tk.NORMAL)
        for fname in files:
            self.listbox.insert(tk.END, fname)

    def show_preview(self, filename):
        path = os.path.join(self.resultados_dir, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                messagebox.showerror('Erro', f'Não foi possível ler: {e}')
                return

        self.preview.delete('1.0', 'end')
        self.preview.insert('1.0', content)

    def on_select(self):
        # Show preview of the first selected file (if any)
        sel = self.listbox.curselection()
        if not sel:
            self.preview.delete('1.0', 'end')
            return
        index = sel[0]
        filename = self.listbox.get(index)
        if filename and not filename.startswith('('):
            self.show_preview(filename)

    def preview_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Info', 'Nenhum arquivo selecionado para pré-visualizar')
            return
        # Show first selected
        filename = self.listbox.get(sel[0])
        if filename and not filename.startswith('('):
            self.show_preview(filename)

    def open_folder(self):
        try:
            import subprocess, sys
            if sys.platform == 'win32':
                subprocess.Popen(f'explorer "{self.resultados_dir}"')
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', self.resultados_dir])
            else:
                subprocess.Popen(['xdg-open', self.resultados_dir])
        except Exception as e:
            messagebox.showerror('Erro', str(e))

    def remove_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Info', 'Nenhum arquivo selecionado para remover')
            return

        files_to_remove = [self.listbox.get(i) for i in sel if not self.listbox.get(i).startswith('(')]
        if not files_to_remove:
            messagebox.showwarning('Aviso', 'Nenhum arquivo válido selecionado')
            return

        confirm = messagebox.askyesno('Confirmar', f'Deseja remover os {len(files_to_remove)} arquivos selecionados?')
        if not confirm:
            return

        errors = []
        for fname in files_to_remove:
            try:
                os.remove(os.path.join(self.resultados_dir, fname))
            except Exception as e:
                errors.append(f'{fname}: {e}')

        self.refresh()
        self.preview.delete('1.0', 'end')
        if errors:
            messagebox.showerror('Erro', '\n'.join(errors))
        else:
            messagebox.showinfo('Sucesso', f'Removido(s): {len(files_to_remove)} arquivo(s)')
