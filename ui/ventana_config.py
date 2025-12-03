import tkinter as tk
from tkinter import messagebox, ttk
from ui.ventana_admin import VentanaAdmin 
from logica.gestor_datos import GestorDatos
from models.grafo_rutas import GrafoRutas
from models.estacion import Estacion
import math

class VentanaConfig:
    def __init__(self, callback_iniciar):
        self.callback = callback_iniciar
        self.gestor = GestorDatos()
        self.grafo = None
        self.root = tk.Tk()
        self.root.title("Launcher - Simulador de Trenes")
        self.root.geometry("700x750")
        self.root.config(bg="#ecf0f1")

        # Título
        lbl_titulo = tk.Label(self.root, text="Bienvenido al Simulador", font=("Arial", 16, "bold"), bg="#ecf0f1")
        lbl_titulo.pack(pady=20)

        # Instrucciones
        lbl_info = tk.Label(self.root, text="Configura el escenario o inicia con los valores guardados.", bg="#ecf0f1")
        lbl_info.pack(pady=5)

        # --- NOTEBOOK (PESTAÑAS) - SIN expand=True ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=False, padx=20, pady=10, side=tk.TOP)

        # Pestaña 1: ADMIN
        frame_admin = ttk.Frame(self.notebook)
        self.notebook.add(frame_admin, text="⚙️ Administrar")
        self._crear_tab_admin(frame_admin)

        # Pestaña 2: RUTAS (NUEVA)
        frame_rutas = ttk.Frame(self.notebook)
        self.notebook.add(frame_rutas, text="🛤️ Rutas")
        self._crear_tab_rutas(frame_rutas)

        # --- BOTONES INFERIORES - SIEMPRE VISIBLES ---
        frame_botones = tk.Frame(self.root, bg="#ecf0f1", height=80)
        frame_botones.pack(side=tk.BOTTOM, pady=15, fill=tk.X, padx=20)
        frame_botones.pack_propagate(False)

        btn_reset = tk.Button(frame_botones, text="🗑️ Restaurar Original", command=self.borrar_datos, 
                              font=("Arial", 10, "bold"), bg="#c0392b", fg="white", width=20)
        btn_reset.pack(side=tk.LEFT, padx=5, pady=5)

        btn_start = tk.Button(frame_botones, text="▶ Iniciar Simulación", command=self.iniciar, 
                              font=("Arial", 12, "bold"), bg="#27ae60", fg="white", width=20, height=2)
        btn_start.pack(side=tk.RIGHT, padx=5, pady=5)

    def _crear_tab_admin(self, parent):
        """Crea la pestaña de administración."""
        btn_admin = tk.Button(parent, text="⚙️ Administrar Datos", command=self.abrir_admin, 
                              font=("Arial", 11, "bold"), bg="#2980B9", fg="white", width=30, height=3)
        btn_admin.pack(pady=50)

    def _crear_tab_rutas(self, parent):
        """Crea la pestaña de configuración de rutas."""
        # Título
        tk.Label(parent, text="Asignar Rutas a Trenes", font=("Arial", 12, "bold")).pack(pady=10)

        # Frame con scroll para los trenes
        canvas = tk.Canvas(parent, bg="white", height=300)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Lista para guardar referencias a los widgets de selección
        self.ruta_widgets = []

        # Cargar datos
        datos = self.gestor.obtener_datos()
        estaciones = datos.get("estaciones", [])
        trenes = datos.get("trenes", [])

        if not estaciones:
            tk.Label(scrollable_frame, text="⚠️ Primero crea estaciones", fg="red").pack(pady=20)
        elif not trenes:
            tk.Label(scrollable_frame, text="⚠️ Primero crea trenes", fg="red").pack(pady=20)
        else:
            # Construir el grafo
            self._construir_grafo_temporal(estaciones)

            # Para cada tren, crear selectores
            for idx, tren in enumerate(trenes):
                frame_tren = tk.LabelFrame(scrollable_frame, text=f"🚂 {tren['id']}", 
                                          font=("Arial", 10, "bold"), padx=10, pady=10)
                frame_tren.pack(fill=tk.X, padx=5, pady=5)

                # Origen
                tk.Label(frame_tren, text="Origen:").grid(row=0, column=0, sticky="w")
                var_origen = tk.StringVar(value=estaciones[0]['id'] if estaciones else "")
                combo_origen = ttk.Combobox(frame_tren, textvariable=var_origen, 
                                           values=[e['id'] for e in estaciones], state="readonly", width=25)
                combo_origen.grid(row=0, column=1, padx=5)

                # Destino
                tk.Label(frame_tren, text="Destino:").grid(row=1, column=0, sticky="w")
                var_destino = tk.StringVar(value=estaciones[1]['id'] if len(estaciones) > 1 else estaciones[0]['id'])
                combo_destino = ttk.Combobox(frame_tren, textvariable=var_destino, 
                                            values=[e['id'] for e in estaciones], state="readonly", width=25)
                combo_destino.grid(row=1, column=1, padx=5)

                # Label para mostrar el camino
                lbl_camino = tk.Label(frame_tren, text="", fg="#2980B9", font=("Arial", 9))
                lbl_camino.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

                # Botón para actualizar preview
                def actualizar_preview(o=var_origen, d=var_destino, l=lbl_camino, t=tren):
                    self._actualizar_preview_ruta(o.get(), d.get(), l, t['id'])

                btn_preview = tk.Button(frame_tren, text="🔍 Ver Camino", command=actualizar_preview,
                                       bg="#3498db", fg="white", width=15)
                btn_preview.grid(row=3, column=0, columnspan=2, pady=5)

                self.ruta_widgets.append({
                    'tren_id': tren['id'],
                    'var_origen': var_origen,
                    'var_destino': var_destino,
                    'lbl_camino': lbl_camino
                })

                # Actualizar preview al iniciar
                actualizar_preview()

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _construir_grafo_temporal(self, estaciones):
        """Construye un grafo temporal para calcular caminos."""
        self.grafo = GrafoRutas()
        
        # Crear estaciones temporales
        mapa_est_temp = {}
        for est_data in estaciones:
            est_obj = Estacion(est_data['id'], 500, x=est_data['x'], y=est_data['y'])
            mapa_est_temp[est_data['id']] = est_obj
            self.grafo.agregar_estacion(est_data['id'], est_obj)

        # Conectar todas con todas
        lista_ids = list(mapa_est_temp.keys())
        for i in range(len(lista_ids)):
            for j in range(i + 1, len(lista_ids)):
                id_a = lista_ids[i]
                id_b = lista_ids[j]
                est_a = mapa_est_temp[id_a]
                est_b = mapa_est_temp[id_b]
                tiempo = self.grafo.calcular_tiempo_entre_estaciones(est_a, est_b)
                self.grafo.agregar_conexion(id_a, id_b, tiempo)

    def _actualizar_preview_ruta(self, id_origen, id_destino, label, tren_id):
        """Calcula y muestra el camino entre dos estaciones."""
        if not self.grafo or not id_origen or not id_destino:
            label.config(text="Selecciona origen y destino")
            return

        try:
            camino, tiempo_total = self.grafo.dijkstra(id_origen, id_destino)
            camino_texto = " → ".join(camino)
            label.config(text=f"Camino: {camino_texto} ({tiempo_total} min total)")
        except Exception as e:
            label.config(text=f"Error: {str(e)}", fg="red")

    def guardar_rutas(self):
        """Guarda las rutas asignadas a los trenes en el gestor."""
        datos = self.gestor.obtener_datos()
        
        # Limpiar rutas previas
        datos['rutas'] = []

        # Guardar nueva configuración de rutas
        for widget in self.ruta_widgets:
            id_origen = widget['var_origen'].get()
            id_destino = widget['var_destino'].get()
            tren_id = widget['tren_id']

            datos['rutas'].append({
                'tren_id': tren_id,
                'origen': id_origen,
                'destino': id_destino
            })

        self.gestor.guardar_configuracion()
        print("✅ Rutas guardadas en configuración")

    def abrir_admin(self):
        VentanaAdmin(self.root)

    def borrar_datos(self):
        """Pregunta y borra la configuración personalizada."""
        respuesta = messagebox.askyesno("Confirmar Restauración", 
                                        "¿Estás seguro de borrar tu configuración personalizada?\n\nSe cargará el escenario original.")
        if respuesta:
            self.gestor.borrar_configuracion()
            messagebox.showinfo("Éxito", "Configuración borrada.")
            self.root.destroy()
            # Reiniciar la ventana
            self.__init__(self.callback)
            self.mostrar()

    def iniciar(self):
        self.guardar_rutas()
        self.root.destroy()
        self.callback() 

    def mostrar(self):
        self.root.mainloop()