import tkinter as tk
from config.settings import COLOR_FONDO, COLOR_TEXTO

class VentanaPrincipal(tk.Frame):
    """Frame principal que muestra la simulación."""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_FONDO)
        
        label = tk.Label(
            self, 
            text="VENTANA DE SIMULACIÓN",
            font=("Arial", 16),
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO
        )
        label.pack(pady=20, padx=20)
