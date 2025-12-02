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
        """Dibuja estaciones, rutas y trenes con información de pasajeros."""
        self.canvas.delete("all") # Limpiar pantalla anterior

        # 1. Dibujar Rutas (Líneas)
        for id_ruta, ruta in self.estado.rutas.items():
            if len(ruta.estaciones) > 1:
                coords = []
                for est in ruta.estaciones:
                    coords.append(est.x)
                    coords.append(est.y)
                self.canvas.create_line(coords, fill="gray", width=2, tags="ruta")

        # 2. Dibujar Estaciones (Círculos Azules)
        radio = 15
        for id_est, est in self.estado.estaciones.items():
            x, y = est.x, est.y
            
            # Dibujar círculo
            self.canvas.create_oval(x - radio, y - radio, x + radio, y + radio, fill="#3498db", outline="black")
            
            # --- CAMBIO AQUÍ: Mostrar nombre y cuántos esperan ---
            cant_esperando = len(est.andenes)
            texto_est = f"{est.nombre}\n(Esp: {cant_esperando})"
            
            # Ponemos el texto un poco más arriba para que no tape el círculo
            self.canvas.create_text(x, y - radio - 20, text=texto_est, font=("Arial", 10, "bold"), justify=tk.CENTER)

        # 3. Dibujar Trenes (Cuadrados Rojos)
        
        lado = 10
        for id_tren, tren in self.estado.trenes.items():
            x, y = 0, 0
            
            if tren.en_estacion:
                est = tren.obtener_estacion_actual()
                if est:
                    x, y = est.x, est.y
            elif tren.ruta_actual:
                # Obtenemos origen y destino BASADO EN EL SENTIDO
                idx_origen = tren.indice_estacion_actual
                idx_destino = idx_origen + tren.sentido # <--- AQUÍ ESTÁ LA CLAVE
                
                estaciones = tren.ruta_actual.estaciones
                
                # Validación de seguridad
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
            # Dibujar si tenemos posición
            if x != 0 and y != 0:
                self.canvas.create_rectangle(x - lado, y - lado, x + lado, y + lado, fill="red", outline="black")
                
                # --- CAMBIO AQUÍ: Mostrar Pasajeros a bordo / Capacidad ---
                cant_abordo = len(tren.pasajeros)
                texto_tren = f"T{tren.id}\n({cant_abordo}/{tren.capacidad})"
                
                self.canvas.create_text(x, y - lado - 15, text=texto_tren, font=("Arial", 8, "bold"), fill="red")

    def avanzar_simulacion(self):
        """Conecta el botón con la lógica."""
        self.estado.avanzar_tiempo(segundos=60) # Avanza 1 minuto
        self.lbl_tiempo.config(text=f"Tiempo: {self.estado.tiempo_actual.strftime('%H:%M:%S')}")
        self.dibujar_mapa()

    def iniciar(self):
        """Arranca la GUI."""
        self.dibujar_mapa()
        self.root.mainloop()