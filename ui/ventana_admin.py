import tkinter as tk
from tkinter import ttk, messagebox
from logica.gestor_datos import GestorDatos
# Importamos tus configuraciones de estilo
from config.settings import *

class VentanaAdmin(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Administración del Sistema")
        
        # Tamaño y Color de fondo
        self.geometry("600x500") 
        self.configure(bg=COLOR_FONDO)

        self.gestor = GestorDatos()

        # --- ESTILOS (Theming) ---
        style = ttk.Style()
        style.theme_use('clam') 
        
        # Configurar pestañas con tus colores
        style.configure("TNotebook", background=COLOR_FONDO, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_BARRA_LATERAL, foreground="white")
        style.map("TNotebook.Tab", background=[("selected", COLOR_BOTON)])
        style.configure("TFrame", background=COLOR_FONDO)
        
        # Crear pestañas
        tabControl = ttk.Notebook(self)
        
        self.tab_estaciones = ttk.Frame(tabControl)
        self.tab_trenes = ttk.Frame(tabControl)
        self.tab_rutas = ttk.Frame(tabControl)
        
        tabControl.add(self.tab_estaciones, text='Estaciones y Vías')
        tabControl.add(self.tab_trenes, text='Trenes')
        tabControl.add(self.tab_rutas, text='Rutas')
        
        tabControl.pack(expand=1, fill="both", padx=10, pady=10)

        # Inicializar contenidos
        self.crear_ui_estaciones()
        self.crear_ui_trenes()
        # Rutas queda pendiente o simple por ahora
        tk.Label(self.tab_rutas, text="Gestión de Rutas (Próximamente)", bg=COLOR_FONDO).pack(pady=20)

    def _crear_label(self, parent, texto, row, col):
        """Helper para crear etiquetas con TUS colores"""
        lbl = tk.Label(parent, text=texto, bg=COLOR_FONDO, fg=COLOR_TEXTO, font=("Arial", 10, "bold"))
        lbl.grid(row=row, column=col, sticky="e", padx=5, pady=5)
    
    def _crear_boton(self, parent, texto, comando, row, col):
        """Helper para crear botones con TUS colores"""
        btn = tk.Button(parent, text=texto, command=comando, 
                        bg=COLOR_BOTON, fg="white",
                        activebackground=COLOR_BARRA_LATERAL, activeforeground="white",
                        font=("Arial", 10, "bold"), bd=0, padx=15, pady=5)
        btn.grid(row=row, column=col, pady=15)

    def crear_ui_estaciones(self):
        # Frame para inputs
        frame_input = tk.Frame(self.tab_estaciones, bg=COLOR_FONDO)
        frame_input.pack(pady=10)

        self._crear_label(frame_input, "ID/Nombre:", 0, 0)
        self.entry_est_nombre = tk.Entry(frame_input)
        self.entry_est_nombre.grid(row=0, column=1)

        self._crear_label(frame_input, "Nº Vías:", 1, 0)
        self.entry_est_vias = tk.Entry(frame_input)
        self.entry_est_vias.grid(row=1, column=1)
        
        self._crear_label(frame_input, "Pos X:", 2, 0)
        self.entry_est_x = tk.Entry(frame_input)
        self.entry_est_x.grid(row=2, column=1)
        
        self._crear_label(frame_input, "Pos Y:", 3, 0)
        self.entry_est_y = tk.Entry(frame_input)
        self.entry_est_y.grid(row=3, column=1)

        self._crear_boton(frame_input, "Agregar Estación", self.accion_agregar_estacion, 4, 1)

        # Lista
        self.lista_estaciones = tk.Listbox(self.tab_estaciones, bg="white", fg=COLOR_TEXTO)
        self.lista_estaciones.pack(fill="both", expand=True, padx=10, pady=10)
        self.refrescar_lista_estaciones()

    def accion_agregar_estacion(self):
        nombre = self.entry_est_nombre.get()
        vias = self.entry_est_vias.get()
        x = self.entry_est_x.get()
        y = self.entry_est_y.get()
        
        if nombre and vias and x and y:
            self.gestor.agregar_estacion(nombre, nombre, vias, x, y)
            self.refrescar_lista_estaciones()
            # Limpiar campos
            self.entry_est_nombre.delete(0, tk.END)
            self.entry_est_vias.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Faltan datos")

    def refrescar_lista_estaciones(self):
        self.lista_estaciones.delete(0, tk.END)
        datos = self.gestor.obtener_datos()["estaciones"]
        for est in datos:
            self.lista_estaciones.insert(tk.END, f"{est['nombre']} (Vías: {est['vias']}) - Pos({est['x']},{est['y']})")

    def crear_ui_trenes(self):
        frame_input = tk.Frame(self.tab_trenes, bg=COLOR_FONDO)
        frame_input.pack(pady=10)
        
        self._crear_label(frame_input, "ID Tren:", 0, 0)
        self.entry_tren_id = tk.Entry(frame_input)
        self.entry_tren_id.grid(row=0, column=1)
        
        self._crear_boton(frame_input, "Agregar Tren", self.accion_agregar_tren, 1, 1)
        
        self.lista_trenes = tk.Listbox(self.tab_trenes, bg="white", fg=COLOR_TEXTO)
        self.lista_trenes.pack(fill="both", expand=True, padx=10, pady=10)
        self.refrescar_lista_trenes()

    def accion_agregar_tren(self):
        tid = self.entry_tren_id.get()
        if tid:
            self.gestor.agregar_tren(tid, 100, 10)
            self.refrescar_lista_trenes()
            self.entry_tren_id.delete(0, tk.END)
    
    def refrescar_lista_trenes(self):
        self.lista_trenes.delete(0, tk.END)
        for t in self.gestor.obtener_datos()["trenes"]:
            self.lista_trenes.insert(tk.END, f"Tren {t['id']}")
        