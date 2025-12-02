import tkinter as tk
from tkinter import messagebox

class VentanaConfig:
    def __init__(self, callback_iniciar):
        """
        :param callback_iniciar: Función que se ejecutará al presionar el botón.
        """
        self.callback = callback_iniciar
        self.root = tk.Tk()
        self.root.title("Launcher - Simulador de Trenes")
        self.root.geometry("400x300")
        self.root.config(bg="#ecf0f1")

        # Título de bienvenida
        lbl_titulo = tk.Label(self.root, text="Bienvenido al Simulador", font=("Arial", 16, "bold"), bg="#ecf0f1")
        lbl_titulo.pack(pady=40)

        # Instrucciones breves
        lbl_info = tk.Label(self.root, text="Presiona el botón para cargar\nel escenario por defecto.", bg="#ecf0f1")
        lbl_info.pack(pady=10)

        # Botón grande para iniciar
        btn_start = tk.Button(self.root, text="Iniciar Simulación", command=self.iniciar, 
                              font=("Arial", 12, "bold"), bg="#27ae60", fg="white", width=20, height=2)
        btn_start.pack(pady=30)

    def iniciar(self):
        """Cierra esta ventana y llama a la función principal."""
        self.root.destroy() # Cerramos el launcher
        self.callback() # Ejecutamos la simulación real

    def mostrar(self):
        self.root.mainloop()
        