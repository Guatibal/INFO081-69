class Tren:
    def __init__(self, id_tren, capacidad_maxima=100, velocidad=10):
        self.id = id_tren
        self.capacidad = capacidad_maxima
        self.velocidad = velocidad 
        
        self.pasajeros = []
        self.ruta_actual = None 
        
        # --- NUEVOS ATRIBUTOS DE ESTADO ---
        self.indice_estacion_actual = 0  # Índice en la lista de estaciones de la ruta
        self.en_estacion = True          # ¿Está detenido bajando/subiendo gente?
        self.tiempo_llegada_estacion = None # Cuándo llegó a la estación
        
        # Progreso en el tramo actual (0.0 a 1.0)
        # 0.0 = Saliendo de estación A
        # 1.0 = Llegando a estación B
        self.progreso_tramo = 0.0 

    def mover(self, delta_tiempo_segundos, tiempo_actual_simulacion):
        """Calcula la nueva posición del tren basado en el tiempo transcurrido."""
        if not self.ruta_actual:
            return

        # Si estamos parados en una estación...
        if self.en_estacion:
            # Aquí podríamos poner lógica de espera (ej. esperar 2 minutos)
            # Por ahora, simulamos que parte inmediatamente
            self.en_estacion = False
            self.progreso_tramo = 0.0
            print(f"Tren {self.id} saliendo de {self.obtener_estacion_actual().nombre}")

        else:
            # Estamos viajando entre estaciones
            tiempos_ruta = self.ruta_actual.tiempos # Lista de tiempos en minutos
            
            # Verificamos si hay tramo siguiente
            if self.indice_estacion_actual < len(tiempos_ruta):
                tiempo_tramo_minutos = tiempos_ruta[self.indice_estacion_actual]
                tiempo_tramo_segundos = tiempo_tramo_minutos * 60
                
                # Cuánto porcentaje del tramo avanzamos en este tick
                avance = delta_tiempo_segundos / tiempo_tramo_segundos
                self.progreso_tramo += avance

                # Si llegamos al 100% (1.0), llegamos a la siguiente estación
                if self.progreso_tramo >= 1.0:
                    self.progreso_tramo = 0.0
                    self.indice_estacion_actual += 1
                    self.en_estacion = True
                    print(f"Tren {self.id} llegó a {self.obtener_estacion_actual().nombre}")
                    
                    # Verificar si terminamos la ruta
                    if self.indice_estacion_actual >= len(self.ruta_actual.estaciones) - 1:
                        # Si es circular, volver al inicio (0)
                        if self.ruta_actual.circular:
                            self.indice_estacion_actual = 0
                        else:
                            # Se queda en la última
                            self.indice_estacion_actual = len(self.ruta_actual.estaciones) - 1

    def obtener_estacion_actual(self):
        """Helper para sacar el objeto estación de la lista."""
        if self.ruta_actual:
            return self.ruta_actual.estaciones[self.indice_estacion_actual]
        return None