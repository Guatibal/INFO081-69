import tkinter as tk
from tkinter import messagebox
# Importamos la ventana de administración para poder abrirla
from ui.ventana_admin import VentanaAdmin 

class VentanaConfig:
    def __init__(self, callback_iniciar):
        """
        :param callback_iniciar: Función que se ejecutará al presionar el botón 'Iniciar'.
        """
        self.callback = callback_iniciar
        self.root = tk.Tk()
        self.root.title("Launcher - Simulador de Trenes")
        # Aumentamos un poco la altura para que quepan los dos botones
        self.root.geometry("400x400") 
        self.root.config(bg="#ecf0f1")

        # Título
        lbl_titulo = tk.Label(self.root, text="Bienvenido al Simulador", font=("Arial", 16, "bold"), bg="#ecf0f1")
        lbl_titulo.pack(pady=30)

        # Instrucciones
        lbl_info = tk.Label(self.root, text="Configura el escenario o inicia con\nlos valores guardados.", bg="#ecf0f1")
        lbl_info.pack(pady=5)

        # --- BOTÓN ADMINISTRAR (NUEVO) ---
        # Este es el botón que te faltaba
        btn_admin = tk.Button(self.root, text="⚙️ Administrar Datos", command=self.abrir_admin, 
                              font=("Arial", 11, "bold"), bg="#2980B9", fg="white", width=20, height=2)
        btn_admin.pack(pady=10)

        # --- BOTÓN INICIAR ---
        btn_start = tk.Button(self.root, text="▶ Iniciar Simulación", command=self.iniciar, 
                              font=("Arial", 12, "bold"), bg="#27ae60", fg="white", width=20, height=2)
        btn_start.pack(pady=20)

    def abrir_admin(self):
        """Abre la ventana de administración sin cerrar el launcher."""
        # Le pasamos 'self.root' como padre
        VentanaAdmin(self.root)

    def iniciar(self):
        """Cierra esta ventana y llama a la función principal."""
        self.root.destroy() # Cerramos el launcher
        self.callback() # Ejecutamos la simulación real

    def mostrar(self):
        self.root.mainloop()