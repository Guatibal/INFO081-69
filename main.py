import tkinter as tk
from config.settings import TAMANO_VENTANA, COLOR_FONDO, COLOR_TEXTO

app = tk.Tk()
app.title("Simulador de Trenes EFE")

app.geometry(TAMANO_VENTANA)

app.configure(bg=COLOR_FONDO)

etiqueta = tk.Label(
    app,
    text="¡Bienvenido al Simulador!",
    font=("Arial", 20),
    bg=COLOR_FONDO,   
    fg=COLOR_TEXTO
)
etiqueta.pack(pady=50)

app.mainloop()
