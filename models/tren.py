class Tren:
    def __init__(self, id_tren, capacidad_maxima=100, velocidad=10):
        self.id = id_tren
        self.capacidad = capacidad_maxima
        self.velocidad = velocidad 
        
        self.pasajeros = []
        self.ruta_actual = None 
        
        # --- ESTADO DE MOVIMIENTO ---
        self.indice_estacion_actual = 0  
        self.en_estacion = True          
        self.progreso_tramo = 0.0
        
        # 1 = Hacia adelante (0 -> 1 -> 2)
        # -1 = Hacia atrás (2 -> 1 -> 0)
        self.sentido = 1 
        
        # --- ESTADO DE ALMUERZO ---
        self.debe_pausarse_por_almuerzo = False  # Flag para detenerse en próxima estación
        self.pausado_por_almuerzo = False         # Flag cuando ya está pausado

    def mover(self, delta_tiempo_segundos, tiempo_actual_simulacion):
        if not self.ruta_actual:
            return

        # --- VALIDACIÓN: Si está pausado por almuerzo, no se mueve ---
        if self.pausado_por_almuerzo:
            return

        # --- FASE 1: SALIR DE LA ESTACIÓN ---
        if self.en_estacion:
            # Si debe pausarse por almuerzo, se queda en la estación
            if self.debe_pausarse_por_almuerzo:
                self.pausado_por_almuerzo = True
                self.debe_pausarse_por_almuerzo = False
                print(f"🍽️  Tren {self.id} pausado en {self.obtener_estacion_actual().nombre} por hora de almuerzo")
                return
            
            # Revisar si llegamos a un extremo para cambiar de sentido
            # Si estamos en la primera (0) -> Vamos hacia adelante (1)
            if self.indice_estacion_actual == 0:
                self.sentido = 1
            # Si estamos en la última -> Vamos hacia atrás (-1)
            elif self.indice_estacion_actual == len(self.ruta_actual.estaciones) - 1:
                self.sentido = -1
            
            self.en_estacion = False
            self.progreso_tramo = 0.0
            print(f"Tren {self.id} saliendo de {self.obtener_estacion_actual().nombre} (Sentido: {self.sentido})")

        # --- FASE 2: VIAJAR ---
        else:
            tiempos = self.ruta_actual.tiempos
            
            # Determinamos qué tiempo usar.
            # Si voy de 0 a 1, uso el tramo 0.
            # Si voy de 1 a 0, uso el tramo 0 también (es el mismo cable).
            # Regla: Usamos el índice menor de las dos estaciones.
            siguiente_idx = self.indice_estacion_actual + self.sentido
            idx_tramo = min(self.indice_estacion_actual, siguiente_idx)
            
            if 0 <= idx_tramo < len(tiempos):
                tiempo_tramo_minutos = tiempos[idx_tramo]
                tiempo_tramo_segundos = tiempo_tramo_minutos * 60
                
                avance = delta_tiempo_segundos / tiempo_tramo_segundos
                self.progreso_tramo += avance

                # LLEGADA
                if self.progreso_tramo >= 1.0:
                    self.progreso_tramo = 0.0
                    self.indice_estacion_actual = siguiente_idx
                    self.en_estacion = True
                    print(f"Tren {self.id} llegó a {self.obtener_estacion_actual().nombre}")

    def obtener_estacion_actual(self):
        if self.ruta_actual:
            return self.ruta_actual.estaciones[self.indice_estacion_actual]
        return None

    # --- GESTIÓN DE PASAJEROS ---
    def subir_pasajero(self, pasajero):
        if len(self.pasajeros) < self.capacidad:
            self.pasajeros.append(pasajero)
            return True
        return False

    def bajar_pasajeros_en_estacion(self, id_estacion):
        bajan = []
        se_quedan = []
        for p in self.pasajeros:
            if p.destino == id_estacion:
                bajan.append(p)
            else:
                se_quedan.append(p)
        self.pasajeros = se_quedan
        return bajan

    def __repr__(self):
        return f"Tren({self.id})"