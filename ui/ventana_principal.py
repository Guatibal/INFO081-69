import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from logica.sistema_guardado import SistemaGuardado

class VentanaPrincipal:
    def __init__(self, estado_simulacion):
        self.estado = estado_simulacion
        self.root = tk.Tk()
        self.root.title("Simulador de Trenes - Grupo INFO081")
        self.root.geometry("1100x700")

        self.ejecutando = True 
        self.velocidad_refresco = 1000 

        # ZOOM / PAN
        self.zoom_factor = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
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

        # 1. EL MAPA (Izquierda)
        self.canvas = tk.Canvas(self.frame_central, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind para zoom con rueda y pan con botón central (Windows)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        self.canvas.bind("<ButtonPress-2>", self._start_pan)
        self.canvas.bind("<B2-Motion>", self._do_pan)
        self.canvas.bind("<ButtonPress-3>", self._start_pan)
        self.canvas.bind("<B3-Motion>", self._do_pan)

        # 2. LA BITÁCORA (Derecha)
        self.frame_bitacora = tk.Frame(self.frame_central, bg="#34495E", width=300)
        self.frame_bitacora.pack(side=tk.RIGHT, fill=tk.Y)
        self.frame_bitacora.pack_propagate(False) 

        tk.Label(self.frame_bitacora, text="📋 BITÁCORA DE VIAJE", 
                 bg="#34495E", fg="white", font=("Arial", 10, "bold"), pady=10).pack()

        self.txt_log = scrolledtext.ScrolledText(self.frame_bitacora, width=30, height=20, 
                                                 bg="#2C3E50", fg="#ECF0F1", font=("Consolas", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
            self.actualizar_bitacora()
        
        self.root.after(self.velocidad_refresco, self.bucle_simulacion)

    def actualizar_bitacora(self):
        if hasattr(self.estado, 'logs_pendientes') and self.estado.logs_pendientes:
            for mensaje in self.estado.logs_pendientes:
                self.imprimir_log(mensaje)
            self.estado.logs_pendientes.clear()

    def imprimir_log(self, texto):
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.insert(tk.END, texto + "\n")
        self.txt_log.config(state=tk.DISABLED)
        self.txt_log.see(tk.END)

    def alternar_pausa(self):
        self.ejecutando = not self.ejecutando
        if self.ejecutando:
            self.btn_pausa.config(text="⏸ Pausar", bg="#e67e22")
            self.imprimir_log(">>> SIMULACIÓN REANUDADA")
        else:
            self.btn_pausa.config(text="▶ Reanudar", bg="#27ae60")
            self.imprimir_log(">>> SIMULACIÓN PAUSADA")

    def dibujar_mapa(self):
        """Dibuja el mapa con rieles SOLO entre estaciones conectadas."""
        self.canvas.delete("all")

        self.canvas.update_idletasks()
        alto = self.canvas.winfo_height() or 1
        ancho = self.canvas.winfo_width() or 1

        def aplicar_transform(x_logico, y_logico):
            x_screen = (x_logico + self.offset_x) * self.zoom_factor
            y_screen = alto - ((y_logico + self.offset_y) * self.zoom_factor)
            return x_screen, y_screen

        # --- DIBUJAR RIELES SOLO ENTRE ESTACIONES CONECTADAS EN RUTAS ---
        rieles_dibujados = set()  # Evitar duplicados
        
        for id_ruta, ruta in self.estado.rutas.items():
            if len(ruta.estaciones) > 1:
                # Dibujamos cada segmento de la ruta
                for i in range(len(ruta.estaciones) - 1):
                    est_a = ruta.estaciones[i]
                    est_b = ruta.estaciones[i + 1]
                    
                    # Crear una clave única para evitar duplicados
                    clave = tuple(sorted([est_a.id, est_b.id]))
                    
                    if clave not in rieles_dibujados:
                        rieles_dibujados.add(clave)
                        
                        x1, y1 = aplicar_transform(est_a.x, est_a.y)
                        x2, y2 = aplicar_transform(est_b.x, est_b.y)
                        
                        # Dibujar línea de riel
                        self.canvas.create_line(x1, y1, x2, y2, fill="#888888", width=max(2, int(3 * self.zoom_factor)), tags="riel")
                        
                        # Pequeñas cruces para simular traviesas (decorativo)
                        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                        self.canvas.create_line(mid_x - 3, mid_y - 3, mid_x + 3, mid_y + 3, fill="#666666", width=1)
                        self.canvas.create_line(mid_x - 3, mid_y + 3, mid_x + 3, mid_y - 3, fill="#666666", width=1)

        # --- DIBUJAR ESTACIONES ---
        radio = 15 * self.zoom_factor
        for id_est, est in self.estado.estaciones.items():
            x, y = aplicar_transform(est.x, est.y)
            r = max(2, radio)
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#3498db", outline="black", width=2)
            cant_esperando = len(getattr(est, "andenes", []))
            texto_est = f"{est.nombre}\n(Esp: {cant_esperando})"
            self.canvas.create_text(x, y - r - (20 * self.zoom_factor), text=texto_est, 
                                   font=("Arial", max(6, int(10 * self.zoom_factor)), "bold"), justify=tk.CENTER)

        # --- DIBUJAR TRENES ---
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
                self.canvas.create_rectangle(x - lado, y - lado, x + lado, y + lado, fill="red", outline="darkred", width=2)
                cant_abordo = len(getattr(tren, "pasajeros", []))
                texto_tren = f"T{getattr(tren, 'id', '')}\n({cant_abordo}/{getattr(tren, 'capacidad', '')})"
                self.canvas.create_text(x, y - lado - (15 * self.zoom_factor), text=texto_tren, 
                                       font=("Arial", max(6, int(8 * self.zoom_factor)), "bold"), fill="darkred")

    def guardar_partida(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".sim", filetypes=[("Archivos", "*.sim")])
        if ruta:
            self.ejecutando = False
            if SistemaGuardado.guardar_estado(self.estado, ruta):
                messagebox.showinfo("Multiverso", "Guardado OK")
                self.imprimir_log(f">>> PARTIDA GUARDADA EN {ruta}")

    def cargar_partida(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos de Simulacion", "*.sim"), ("Todos", "*.*")],
            title="Cargar Línea Temporal"
        )
        if ruta:
            nuevo_estado = SistemaGuardado.cargar_estado(ruta)
            if nuevo_estado:
                # 1. Reemplazamos el cerebro de la simulación
                self.estado = nuevo_estado
                
                # 2. Actualizamos gráficos y tiempo
                self.lbl_tiempo.config(text=f"Tiempo: {self.estado.tiempo_actual}")
                self.dibujar_mapa()
                
                # 3. RESTAURAR LA BITÁCORA (Aquí está la magia)
                self.txt_log.config(state=tk.NORMAL) # Desbloquear
                self.txt_log.delete(1.0, tk.END)     # Borrar texto actual
                
                # Verificamos si el archivo guardado tiene historial (por compatibilidad)
                if hasattr(self.estado, 'historial_logs'):
                    for linea in self.estado.historial_logs:
                        self.txt_log.insert(tk.END, linea + "\n")
                
                self.txt_log.see(tk.END) # Bajar scroll al final
                self.txt_log.config(state=tk.DISABLED) # Bloquear de nuevo

                # 4. Pausamos y avisamos
                self.ejecutando = False
                self.btn_pausa.config(text="▶ Reanudar", bg="#27ae60")
                messagebox.showinfo("Multiverso", "¡Viaje en el tiempo completado!\nBitácora restaurada.")
            else:
                messagebox.showerror("Error", "Archivo corrupto.")

    def zoom(self, factor, cx=None, cy=None):
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

        world_x = (cx / old_zoom) - self.offset_x
        world_y = ((alto - cy) / old_zoom) - self.offset_y

        self.zoom_factor = new_zoom

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
        if hasattr(event, 'delta'):
            if event.delta > 0:
                factor = 1.15
            else:
                factor = 1/1.15
            self.zoom(factor, cx=event.x, cy=event.y)
        else:
            if event.num == 4:
                self.zoom(1.15, cx=event.x, cy=event.y)
            elif event.num == 5:
                self.zoom(1/1.15, cx=event.x, cy=event.y)

    def _start_pan(self, event):
        self._pan_start = (event.x, event.y)
        self._pan_offset_backup = (self.offset_x, self.offset_y)

    def _do_pan(self, event):
        if not self._pan_start:
            return
        start_x, start_y = self._pan_start
        dx = event.x - start_x
        dy = event.y - start_y
        self.offset_x = self._pan_offset_backup[0] + (dx / max(1e-6, self.zoom_factor))
        self.offset_y = self._pan_offset_backup[1] - (dy / max(1e-6, self.zoom_factor))
        self.dibujar_mapa()