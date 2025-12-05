"""
Tema e constantes compartilhadas para a GUI
"""
PALETA = {
    "fundo_escuro": "#2a2f3f",
    "fundo_claro": "#3a3f4f",
    "header": "#1f2330",
    "accent": "#a78bfa",
    "texto_principal": "#e8e4f3",
    "texto_secundario": "#b8b0d0",
    "botao_primario": "#8b5cf6",
    "botao_secundario": "#6d28d9",
    "botao_hover": "#a78bfa",
    "sucesso": "#86efac",
    "atencao": "#fbbf24",
    "erro": "#f87171"
}

def apply_customtkinter_theme(ctk):
    """Aplica algumas configurações padrão ao customtkinter (chamado pela GUI)."""
    try:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    except Exception:
        pass
