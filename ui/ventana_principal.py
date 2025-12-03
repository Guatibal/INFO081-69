import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from logica.sistema_guardado import SistemaGuardado

class VentanaPrincipal:
    def __init__(self, estado_simulacion):
        self.estado = estado_simulacion
        self.root = tk.Tk()
        self.root.title("Simulador de Trenes - Grupo INFO081")
        self.root.geometry("1100x700") # Un poco más ancho para que quepa la bitácora

        self.ejecutando = True 
        self.velocidad_refresco = 1000 

        # ZOOM / PAN
        self.zoom_factor = 1.0
        self.offset_x = 0.0    # desplazamiento lógico en X
        self.offset_y = 0.0    # desplazamiento lógico en Y
        self._pan_start = None
        self._pan_offset_backup = (0.0, 0.0)

        # --- PANEL SUPERIOR (CONTROLES) ---
        self.frame_controles = tk.Frame(self.root, bg="#dddddd", pady=10)
        self.frame_controles.pack(side=tk.TOP, fill=tk.X)

        self.btn_pausa = tk.Button(self.frame_controles, text="⏸ Pausar", command=self.alternar_pausa, 
                                   bg="#e67e22", fg="white", font=("Arial", 10, "bold"), width=12)
        self.btn_pausa.pack(side=tk.LEFT, padx=20)
        
        self.lbl_tiempo = tk.Label(self.frame_controles, text=f"Tiempo: {self.estado.tiempo_actual}", font=("Arial", 12))
        self.lbl_tiempo.pack(side=tk.LEFT, padx=20)

        self.btn_guardar = tk.Button(self.frame_controles, text="💾 Guardar", command=self.guardar_partida, bg="#f39c12", fg="white")
        self.btn_guardar.pack(side=tk.LEFT, padx=5)

        self.btn_cargar = tk.Button(self.frame_controles, text="📂 Cargar", command=self.cargar_partida, bg="#2980B9", fg="white")
        self.btn_cargar.pack(side=tk.LEFT, padx=5)

        # ZOOM CONTROLS
        self.btn_zoom_in = tk.Button(self.frame_controles, text="＋", command=self.zoom_in, width=3)
        self.btn_zoom_in.pack(side=tk.LEFT, padx=5)
        self.btn_zoom_out = tk.Button(self.frame_controles, text="－", command=self.zoom_out, width=3)
        self.btn_zoom_out.pack(side=tk.LEFT)
        self.btn_zoom_reset = tk.Button(self.frame_controles, text="Reset", command=self.reset_zoom, width=6)
        self.btn_zoom_reset.pack(side=tk.LEFT, padx=8)

        # pequeña nota de uso para el usuario
        tk.Label(self.frame_controles, text="Rueda: zoom  ·  click derecho: mover", 
                 bg="#dddddd", fg="#333333", font=("Arial", 9)).pack(side=tk.LEFT, padx=12)

        # --- AREA CENTRAL (DIVIDIDA EN DOS) ---
        self.frame_central = tk.Frame(self.root)
        self.frame_central.pack(fill=tk.BOTH, expand=True)

        # 1. EL MAPA (Izquierda) - Ocupa el 75% del ancho
        self.canvas = tk.Canvas(self.frame_central, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind para zoom con rueda y pan con botón central (Windows)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)           # Windows
        self.canvas.bind("<Button-4>", self._on_mousewheel)            # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mousewheel)            # Linux scroll down
        self.canvas.bind("<ButtonPress-2>", self._start_pan)           # Middle button press
        self.canvas.bind("<B2-Motion>", self._do_pan)                  # Middle button drag
        # También permitir pan con botón derecho + Shift (por si no hay botón central)
        self.canvas.bind("<ButtonPress-3>", self._start_pan)
        self.canvas.bind("<B3-Motion>", self._do_pan)

        # 2. LA BITÁCORA (Derecha) - Panel lateral
        self.frame_bitacora = tk.Frame(self.frame_central, bg="#34495E", width=300)
        self.frame_bitacora.pack(side=tk.RIGHT, fill=tk.Y)
        # Evita que el frame se achique si no hay texto
        self.frame_bitacora.pack_propagate(False) 

        # Título de la bitácora
        tk.Label(self.frame_bitacora, text="📋 BITÁCORA DE VIAJE", 
                 bg="#34495E", fg="white", font=("Arial", 10, "bold"), pady=10).pack()

        # Cuadro de texto con scroll
        self.txt_log = scrolledtext.ScrolledText(self.frame_bitacora, width=30, height=20, 
                                                 bg="#2C3E50", fg="#ECF0F1", font=("Consolas", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mensaje inicial
        self.imprimir_log("Simulación iniciada...")

    def iniciar(self):
        self.dibujar_mapa()
        self.bucle_simulacion()
        self.root.mainloop()

    def bucle_simulacion(self):
        if self.ejecutando:
            self.estado.avanzar_tiempo(segundos=60)
            self.lbl_tiempo.config(text=f"Tiempo: {self.estado.tiempo_actual}")
            
            self.dibujar_mapa()
            self.actualizar_bitacora() # <--- LEEMOS LOS MENSAJES NUEVOS
        
        self.root.after(self.velocidad_refresco, self.bucle_simulacion)

    def actualizar_bitacora(self):
        """Revisa si la lógica mandó mensajes nuevos y los pone en el texto."""
        # Verificamos si existe la lista (por si acaso)
        if hasattr(self.estado, 'logs_pendientes') and self.estado.logs_pendientes:
            # Recorremos todos los mensajes pendientes
            for mensaje in self.estado.logs_pendientes:
                self.imprimir_log(mensaje)
            # Limpiamos la lista para no repetir mensajes
            self.estado.logs_pendientes.clear()

    def imprimir_log(self, texto):
        """Escribe en la caja de texto y baja el scroll automáticamente."""
        self.txt_log.config(state=tk.NORMAL) # Habilitar escritura
        self.txt_log.insert(tk.END, texto + "\n")
        self.txt_log.config(state=tk.DISABLED) # Bloquear para que el usuario no borre
        self.txt_log.see(tk.END) # Auto-scroll al final

    def alternar_pausa(self):
        self.ejecutando = not self.ejecutando
        if self.ejecutando:
            self.btn_pausa.config(text="⏸ Pausar", bg="#e67e22")
            self.imprimir_log(">>> SIMULACIÓN REANUDADA")
        else:
            self.btn_pausa.config(text="▶ Reanudar", bg="#27ae60")
            self.imprimir_log(">>> SIMULACIÓN PAUSADA")

    def dibujar_mapa(self):
        # ... (TU CÓDIGO DE DIBUJO DE SIEMPRE - AHORA CON ZOOM/PAN) ...
        self.canvas.delete("all")

        # Aseguramos que el canvas tenga tamaño actualizado y obtenemos su alto
        self.canvas.update_idletasks()
        alto = self.canvas.winfo_height() or 1
        ancho = self.canvas.winfo_width() or 1

        # Transformación: de coordenadas lógicas (x,y) -> coordenadas de canvas teniendo en cuenta zoom y offset.
        def aplicar_transform(x_logico, y_logico):
            # Primero aplicamos offset en coordenadas lógicas, luego escala, y finalmente invertimos Y para canvas.
            x_screen = (x_logico + self.offset_x) * self.zoom_factor
            y_screen = alto - ((y_logico + self.offset_y) * self.zoom_factor)
            return x_screen, y_screen

        for id_ruta, ruta in self.estado.rutas.items():
            if len(ruta.estaciones) > 1:
                coords = []
                for est in ruta.estaciones:
                    xs, ys = aplicar_transform(est.x, est.y)
                    coords.append(xs)
                    coords.append(ys)
                self.canvas.create_line(coords, fill="gray", width=max(1, int(2 * self.zoom_factor)), tags="ruta")

        radio = 15 * self.zoom_factor
        for id_est, est in self.estado.estaciones.items():
            x, y = aplicar_transform(est.x, est.y)
            r = max(2, radio)
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#3498db", outline="black")
            cant_esperando = len(getattr(est, "andenes", []))
            texto_est = f"{est.nombre}\n(Esp: {cant_esperando})"
            self.canvas.create_text(x, y - r - (20 * self.zoom_factor), text=texto_est, font=("Arial", max(6, int(10 * self.zoom_factor)), "bold"), justify=tk.CENTER)

        lado = max(4, 10 * self.zoom_factor)
        for id_tren, tren in self.estado.trenes.items():
            x, y = None, None
            if getattr(tren, "en_estacion", False):
                est = getattr(tren, "obtener_estacion_actual", lambda: None)()
                if est:
                    x, y = aplicar_transform(est.x, est.y)
            elif getattr(tren, "ruta_actual", None):
                idx_origen = getattr(tren, "indice_estacion_actual", 0)
                idx_destino = idx_origen + getattr(tren, "sentido", 1)
                estaciones = tren.ruta_actual.estaciones
                if 0 <= idx_destino < len(estaciones):
                    est_origen = estaciones[idx_origen]
                    est_destino = estaciones[idx_destino]
                    progreso = getattr(tren, "progreso_tramo", 0.0)
                    x_log = est_origen.x + (est_destino.x - est_origen.x) * progreso
                    y_log = est_origen.y + (est_destino.y - est_origen.y) * progreso
                    x, y = aplicar_transform(x_log, y_log)
            if x is not None and y is not None:
                self.canvas.create_rectangle(x - lado, y - lado, x + lado, y + lado, fill="red", outline="black")
                cant_abordo = len(getattr(tren, "pasajeros", []))
                texto_tren = f"T{getattr(tren, 'id', '')}\n({cant_abordo}/{getattr(tren, 'capacidad', '')})"
                self.canvas.create_text(x, y - lado - (15 * self.zoom_factor), text=texto_tren, font=("Arial", max(6, int(8 * self.zoom_factor)), "bold"), fill="red")

    def guardar_partida(self):
        # ... (TU CÓDIGO DE GUARDAR - SIN CAMBIOS) ...
        ruta = filedialog.asksaveasfilename(defaultextension=".sim", filetypes=[("Archivos", "*.sim")])
        if ruta:
            self.ejecutando = False
            if SistemaGuardado.guardar_estado(self.estado, ruta):
                messagebox.showinfo("Multiverso", "Guardado OK")
                self.imprimir_log(f">>> PARTIDA GUARDADA EN {ruta}")

    def cargar_partida(self):
        # ... (TU CÓDIGO DE CARGAR - SIN CAMBIOS) ...
        ruta = filedialog.askopenfilename(filetypes=[("Archivos", "*.sim")])
        if ruta:
            nuevo = SistemaGuardado.cargar_estado(ruta)
            if nuevo:
                self.estado = nuevo
                self.dibujar_mapa()
                self.ejecutando = False
                messagebox.showinfo("Multiverso", "Cargado OK")
                # Necesitamos reiniciar la bitácora en la GUI porque es un objeto nuevo
                self.txt_log.config(state=tk.NORMAL)
                self.txt_log.delete(1.0, tk.END) # Limpiar log anterior
                self.imprimir_log(">>> LÍNEA TEMPORAL CARGADA")

    # ----- ZOOM / PAN HELPERS -----
    def zoom(self, factor, cx=None, cy=None):
        """Aplica zoom multiplicativo centrado en (cx,cy) en coordenadas de pantalla.
           Si cx/cy son None, centra en el centro del canvas.
        """
        self.canvas.update_idletasks()
        alto = self.canvas.winfo_height() or 1
        ancho = self.canvas.winfo_width() or 1

        old_zoom = self.zoom_factor
        new_zoom = max(0.1, min(10.0, self.zoom_factor * factor))
        if new_zoom == old_zoom:
            return

        if cx is None or cy is None:
            cx = ancho / 2
            cy = alto / 2

        # Coordenada lógica que está bajo el cursor antes del zoom
        world_x = (cx / old_zoom) - self.offset_x
        world_y = ((alto - cy) / old_zoom) - self.offset_y

        # Actualizamos el zoom
        self.zoom_factor = new_zoom

        # Ajustamos offset para que el punto bajo el cursor permanezca en la misma posición de pantalla
        self.offset_x = (cx / new_zoom) - world_x
        self.offset_y = ((alto - cy) / new_zoom) - world_y

        self.dibujar_mapa()

    def zoom_in(self):
        self.zoom(1.2)

    def zoom_out(self):
        self.zoom(1/1.2)

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.dibujar_mapa()

    def _on_mousewheel(self, event):
        # Windows: event.delta; Linux: Button-4/5
        if hasattr(event, 'delta'):
            if event.delta > 0:
                factor = 1.15
            else:
                factor = 1/1.15
            # usamos la posición del mouse como centro
            self.zoom(factor, cx=event.x, cy=event.y)
        else:
            # event.num para Linux Button-4/5
            if event.num == 4:
                self.zoom(1.15, cx=event.x, cy=event.y)
            elif event.num == 5:
                self.zoom(1/1.15, cx=event.x, cy=event.y)

    def _start_pan(self, event):
        # iniciar pan: guardamos la posición del mouse y el offset en ese momento
        self._pan_start = (event.x, event.y)
        self._pan_offset_backup = (self.offset_x, self.offset_y)

    def _do_pan(self, event):
        if not self._pan_start:
            return
        start_x, start_y = self._pan_start
        dx = event.x - start_x
        dy = event.y - start_y
        # ajustar offset (las unidades son lógicas, por eso dividimos por zoom)
        self.offset_x = self._pan_offset_backup[0] + (dx / max(1e-6, self.zoom_factor))
        self.offset_y = self._pan_offset_backup[1] - (dy / max(1e-6, self.zoom_factor))
        self.dibujar_mapa()