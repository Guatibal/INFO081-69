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

        # --- AREA CENTRAL (DIVIDIDA EN DOS) ---
        self.frame_central = tk.Frame(self.root)
        self.frame_central.pack(fill=tk.BOTH, expand=True)

        # 1. EL MAPA (Izquierda) - Ocupa el 75% del ancho
        self.canvas = tk.Canvas(self.frame_central, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

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
        # ... (TU CÓDIGO DE DIBUJO DE SIEMPRE - SIN CAMBIOS) ...
        self.canvas.delete("all") 
        for id_ruta, ruta in self.estado.rutas.items():
            if len(ruta.estaciones) > 1:
                coords = []
                for est in ruta.estaciones:
                    coords.append(est.x); coords.append(est.y)
                self.canvas.create_line(coords, fill="gray", width=2, tags="ruta")

        radio = 15
        for id_est, est in self.estado.estaciones.items():
            x, y = est.x, est.y
            self.canvas.create_oval(x - radio, y - radio, x + radio, y + radio, fill="#3498db", outline="black")
            cant_esperando = len(est.andenes)
            texto_est = f"{est.nombre}\n(Esp: {cant_esperando})"
            self.canvas.create_text(x, y - radio - 20, text=texto_est, font=("Arial", 10, "bold"), justify=tk.CENTER)

        lado = 10
        for id_tren, tren in self.estado.trenes.items():
            x, y = 0, 0
            if tren.en_estacion:
                est = tren.obtener_estacion_actual()
                if est: x, y = est.x, est.y
            elif tren.ruta_actual:
                idx_origen = tren.indice_estacion_actual
                idx_destino = idx_origen + tren.sentido 
                estaciones = tren.ruta_actual.estaciones
                if 0 <= idx_destino < len(estaciones):
                    est_origen = estaciones[idx_origen]
                    est_destino = estaciones[idx_destino]
                    x = est_origen.x + (est_destino.x - est_origen.x) * tren.progreso_tramo
                    y = est_origen.y + (est_destino.y - est_origen.y) * tren.progreso_tramo
            if x != 0 and y != 0:
                self.canvas.create_rectangle(x - lado, y - lado, x + lado, y + lado, fill="red", outline="black")
                cant_abordo = len(tren.pasajeros)
                texto_tren = f"T{tren.id}\n({cant_abordo}/{tren.capacidad})"
                self.canvas.create_text(x, y - lado - 15, text=texto_tren, font=("Arial", 8, "bold"), fill="red")

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