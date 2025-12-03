import tkinter as tk
from tkinter import messagebox, filedialog
from logica.sistema_guardado import SistemaGuardado

class VentanaPrincipal:
    def __init__(self, estado_simulacion):
        self.estado = estado_simulacion
        self.root = tk.Tk()
        self.root.title("Simulador de Trenes - Grupo INFO081")
        self.root.geometry("1000x700")

        # Estado del bucle (True = Corriendo, False = Pausado)
        self.ejecutando = True 
        
        # --- CONFIGURACIÓN DE VELOCIDAD ---
        # 1000 milisegundos = 1 segundo real.
        # Esto significa: "Espera 1 segundo real para avanzar el siguiente minuto simulado"
        self.velocidad_refresco = 1000 

        # --- PANEL SUPERIOR (CONTROLES) ---
        self.frame_controles = tk.Frame(self.root, bg="#dddddd", pady=10)
        self.frame_controles.pack(side=tk.TOP, fill=tk.X)

        # Botón Pause/Play
        self.btn_pausa = tk.Button(self.frame_controles, text="⏸ Pausar", command=self.alternar_pausa, 
                                   bg="#e67e22", fg="white", font=("Arial", 10, "bold"), width=12)
        self.btn_pausa.pack(side=tk.LEFT, padx=20)
        
        # Etiqueta de Tiempo
        self.lbl_tiempo = tk.Label(self.frame_controles, text=f"Tiempo: {self.estado.tiempo_actual}", font=("Arial", 12))
        self.lbl_tiempo.pack(side=tk.LEFT, padx=20)

        # Botones Multiverso
        self.btn_guardar = tk.Button(self.frame_controles, text="💾 Guardar", command=self.guardar_partida, bg="#f39c12", fg="white")
        self.btn_guardar.pack(side=tk.LEFT, padx=5)

        self.btn_cargar = tk.Button(self.frame_controles, text="📂 Cargar", command=self.cargar_partida, bg="#2980B9", fg="white")
        self.btn_cargar.pack(side=tk.LEFT, padx=5)

        # Canvas
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def iniciar(self):
        self.dibujar_mapa()
        self.bucle_simulacion()
        self.root.mainloop()

    def bucle_simulacion(self):
        """Bucle principal del juego."""
        if self.ejecutando:
            # 1. Avanzamos 60 segundos en la simulación (1 minuto)
            self.estado.avanzar_tiempo(segundos=60)
            
            # 2. Actualizamos la pantalla
            self.lbl_tiempo.config(text=f"Tiempo: {self.estado.tiempo_actual}")
            self.dibujar_mapa()
        
        # 3. Esperamos 1000ms (1 segundo real) para repetir el ciclo
        self.root.after(self.velocidad_refresco, self.bucle_simulacion)

    def alternar_pausa(self):
        self.ejecutando = not self.ejecutando
        if self.ejecutando:
            self.btn_pausa.config(text="⏸ Pausar", bg="#e67e22")
        else:
            self.btn_pausa.config(text="▶ Reanudar", bg="#27ae60")

    def dibujar_mapa(self):
        self.canvas.delete("all") 

        # Rutas
        for id_ruta, ruta in self.estado.rutas.items():
            if len(ruta.estaciones) > 1:
                coords = []
                for est in ruta.estaciones:
                    coords.append(est.x)
                    coords.append(est.y)
                self.canvas.create_line(coords, fill="gray", width=2, tags="ruta")

        # Estaciones
        radio = 15
        for id_est, est in self.estado.estaciones.items():
            x, y = est.x, est.y
            self.canvas.create_oval(x - radio, y - radio, x + radio, y + radio, fill="#3498db", outline="black")
            
            cant_esperando = len(est.andenes)
            texto_est = f"{est.nombre}\n(Esp: {cant_esperando})"
            self.canvas.create_text(x, y - radio - 20, text=texto_est, font=("Arial", 10, "bold"), justify=tk.CENTER)

        # Trenes
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
        ruta = filedialog.asksaveasfilename(
            defaultextension=".sim",
            filetypes=[("Archivos de Simulacion", "*.sim"), ("Todos", "*.*")],
            title="Guardar Línea Temporal"
        )
        if ruta:
            estado_previo = self.ejecutando
            self.ejecutando = False 
            self.btn_pausa.config(text="▶ Reanudar", bg="#27ae60")
            
            if SistemaGuardado.guardar_estado(self.estado, ruta):
                messagebox.showinfo("Multiverso", "Línea temporal guardada exitosamente.")
            else:
                messagebox.showerror("Error", "No se pudo guardar.")

    def cargar_partida(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos de Simulacion", "*.sim"), ("Todos", "*.*")],
            title="Cargar Línea Temporal"
        )
        if ruta:
            nuevo_estado = SistemaGuardado.cargar_estado(ruta)
            if nuevo_estado:
                self.estado = nuevo_estado
                self.lbl_tiempo.config(text=f"Tiempo: {self.estado.tiempo_actual}")
                self.dibujar_mapa()
                self.ejecutando = False
                self.btn_pausa.config(text="▶ Reanudar", bg="#27ae60")
                messagebox.showinfo("Multiverso", "¡Viaje en el tiempo completado!")
            else:
                messagebox.showerror("Error", "Archivo corrupto.")