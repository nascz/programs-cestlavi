#!/usr/bin/env python3
"""
Launcher simples para OCR GUI
Permite rodar a GUI sem precisar do terminal
"""

import sys
import os

# Adicionar o diretório cdigo ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importar e rodar a GUI
if __name__ == "__main__":
    try:
        import customtkinter as ctk
        from gui_ocr import OCRguiModerna
        
        root = ctk.CTk()
        app = OCRguiModerna(root)
        root.mainloop()
    
    except Exception as e:
        # Se algo der errado, mostrar erro em um dialog
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro ao iniciar", f"Erro: {str(e)}\n\nVerifique se todas as dependências estão instaladas.")
            root.destroy()
        except:
            print(f"Erro: {e}")
        sys.exit(1)
