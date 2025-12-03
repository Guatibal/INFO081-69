import tkinter as tk
from tkinter import messagebox
from ui.ventana_admin import VentanaAdmin 
from logica.gestor_datos import GestorDatos # <--- IMPORTANTE: Agregamos esto

class VentanaConfig:
    def __init__(self, callback_iniciar):
        self.callback = callback_iniciar
        self.root = tk.Tk()
        self.root.title("Launcher - Simulador de Trenes")
        self.root.geometry("400x450") # Un poco más alto para el nuevo botón
        self.root.config(bg="#ecf0f1")

        # Título
        lbl_titulo = tk.Label(self.root, text="Bienvenido al Simulador", font=("Arial", 16, "bold"), bg="#ecf0f1")
        lbl_titulo.pack(pady=20)

        # Instrucciones
        lbl_info = tk.Label(self.root, text="Configura el escenario o inicia con\nlos valores guardados.", bg="#ecf0f1")
        lbl_info.pack(pady=5)

        # --- BOTÓN ADMINISTRAR ---
        btn_admin = tk.Button(self.root, text="⚙️ Administrar Datos", command=self.abrir_admin, 
                              font=("Arial", 11, "bold"), bg="#2980B9", fg="white", width=20, height=2)
        btn_admin.pack(pady=10)

        # --- BOTÓN BORRAR CONFIG (NUEVO) ---
        # Lo ponemos rojo para indicar precaución
        btn_reset = tk.Button(self.root, text="🗑️ Restaurar Original", command=self.borrar_datos, 
                              font=("Arial", 10, "bold"), bg="#c0392b", fg="white", width=20)
        btn_reset.pack(pady=5)

        # --- BOTÓN INICIAR ---
        btn_start = tk.Button(self.root, text="▶ Iniciar Simulación", command=self.iniciar, 
                              font=("Arial", 12, "bold"), bg="#27ae60", fg="white", width=20, height=2)
        btn_start.pack(pady=20)

    def abrir_admin(self):
        VentanaAdmin(self.root)

    def borrar_datos(self):
        """Pregunta y borra la configuración personalizada."""
        respuesta = messagebox.askyesno("Confirmar Restauración", 
                                        "¿Estás seguro de borrar tu configuración personalizada?\n\nSe cargará el escenario original (Central-Norte-Sur).")
        if respuesta:
            gestor = GestorDatos()
            gestor.borrar_configuracion()
            messagebox.showinfo("Éxito", "Configuración borrada. Al iniciar se usará el mapa por defecto.")

    def iniciar(self):
        self.root.destroy()
        self.callback() 

    def mostrar(self):
        self.root.mainloop()