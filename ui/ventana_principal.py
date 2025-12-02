import tkinter as tk
from tkinter import messagebox

class VentanaPrincipal:
    def __init__(self, estado_simulacion):
        self.estado = estado_simulacion
        self.root = tk.Tk()
        self.root.title("Simulador de Trenes - Grupo INFO081")
        self.root.geometry("1000x700")

        # --- PANEL SUPERIOR (CONTROLES) ---
        self.frame_controles = tk.Frame(self.root, bg="#dddddd", pady=10)
        self.frame_controles.pack(side=tk.TOP, fill=tk.X)

        self.btn_avanzar = tk.Button(self.frame_controles, text="Avanzar 1 Tick", command=self.avanzar_simulacion, bg="#4CAF50", fg="white")
        self.btn_avanzar.pack(side=tk.LEFT, padx=20)
        
        self.lbl_tiempo = tk.Label(self.frame_controles, text=f"Tiempo: {self.estado.tiempo_actual}", font=("Arial", 12))
        self.lbl_tiempo.pack(side=tk.LEFT, padx=20)

        # --- AREA DE DIBUJO (CANVAS) ---
        # Aquí dibujaremos el mapa (RF03)
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def dibujar_mapa(self):
        """Dibuja estaciones, rutas y trenes basado en el estado actual."""
        self.canvas.delete("all") # Limpiar pantalla anterior

        # 1. Dibujar Rutas (Líneas entre estaciones)
        # Nota: Esto requiere que las rutas tengan estaciones asignadas
        for id_ruta, ruta in self.estado.rutas.items():
            if len(ruta.estaciones) > 1:
                # Dibujamos líneas conectando las estaciones de la ruta
                coords = []
                for est in ruta.estaciones:
                    coords.append(est.x)
                    coords.append(est.y)
                # create_line pide x1, y1, x2, y2, ...
                self.canvas.create_line(coords, fill="gray", width=2, tags="ruta")

        # 2. Dibujar Estaciones (Círculos)
        radio = 15
        for id_est, est in self.estado.estaciones.items():
            x, y = est.x, est.y
            self.canvas.create_oval(x - radio, y - radio, x + radio, y + radio, fill="#3498db", outline="black")
            self.canvas.create_text(x, y - radio - 10, text=est.nombre, font=("Arial", 10, "bold"))

        # 3. Dibujar Trenes (Cuadrados rojos)
        lado = 10
        for id_tren, tren in self.estado.trenes.items():
            x, y = 0, 0
            
            # CASO A: El tren está quieto en una estación
            if tren.en_estacion:
                est = tren.obtener_estacion_actual()
                if est:
                    x, y = est.x, est.y
            
            # CASO B: El tren está viajando entre dos estaciones
            elif tren.ruta_actual:
                # Obtenemos Estación Origen (donde estaba) y Destino (a donde va)
                idx_origen = tren.indice_estacion_actual
                # Nota: El destino es el índice siguiente
                idx_destino = idx_origen + 1
                
                # Manejo de ruta circular para evitar error de índice
                estaciones = tren.ruta_actual.estaciones
                if idx_destino >= len(estaciones) and tren.ruta_actual.circular:
                    idx_destino = 0
                
                if idx_destino < len(estaciones):
                    est_origen = estaciones[idx_origen]
                    est_destino = estaciones[idx_destino]
                    
                    # Interpolación Lineal: Fórmula matemática para hallar punto medio
                    # X = X_inicio + (X_fin - X_inicio) * progreso
                    x = est_origen.x + (est_destino.x - est_origen.x) * tren.progreso_tramo
                    y = est_origen.y + (est_destino.y - est_origen.y) * tren.progreso_tramo
            
            # Dibujamos solo si calculamos una posición válida
            if x != 0 and y != 0:
                self.canvas.create_rectangle(x - lado, y - lado, x + lado, y + lado, fill="red")
                self.canvas.create_text(x, y - lado - 5, text=f"T{tren.id}", font=("Arial", 8, "bold"))

    def avanzar_simulacion(self):
        """Conecta el botón con la lógica."""
        self.estado.avanzar_tiempo(segundos=60) # Avanza 1 minuto
        self.lbl_tiempo.config(text=f"Tiempo: {self.estado.tiempo_actual.strftime('%H:%M:%S')}")
        self.dibujar_mapa()

    def iniciar(self):
        """Arranca la GUI."""
        self.dibujar_mapa()
        self.root.mainloop()