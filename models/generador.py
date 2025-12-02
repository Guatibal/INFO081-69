import random
from .pasajero import Pasajero

class GeneradorPasajeros:
    def __init__(self, estacion_origen, lista_estaciones_destino):
        """
        :param estacion_origen: ID de la estación donde nacen los pasajeros.
        :param lista_estaciones_destino: Lista de IDs de posibles destinos.
        """
        self.origen = estacion_origen
        self.destinos = lista_estaciones_destino
        self.contador_id = 0
        
        # Tasa de llegada: 1 pasajero cada X ticks (aprox)
        self.tasa_llegada = 0.1 # 10% de probabilidad por tick

    def generar(self, tiempo_actual):
        """
        Intenta crear pasajeros en este instante de tiempo.
        Retorna una lista de nuevos pasajeros (puede estar vacía).
        """
        nuevos = []
        
        # Lógica simple: tirar un dado
        if random.random() < self.tasa_llegada:
            if not self.destinos:
                return []
                
            # Elegir un destino al azar diferente al origen
            destino = random.choice(self.destinos)
            if destino == self.origen:
                return [] # Nadie viaja a donde ya está

            self.contador_id += 1
            # Creamos un ID único tipo "P-Central-1"
            id_pasajero = f"P-{self.origen}-{self.contador_id}"
            
            p = Pasajero(id_pasajero, self.origen, destino, tiempo_actual)
            nuevos.append(p)
            
        return nuevos