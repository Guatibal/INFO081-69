import tkinter as tk
from config.settings import COLOR_FONDO, COLOR_TEXTO

class VentanaConfig(tk.Frame):
    """Frame para configurar trenes, rutas y estaciones (CRUD)."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_FONDO)
        
        label = tk.Label(
            self, 
            text="VENTANA DE CONFIGURACIÓN (CRUD)",
            font=("Arial", 16),
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO
        )
        label.pack(pady=20, padx=20)
