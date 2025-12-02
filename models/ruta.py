class Ruta:
    def __init__(self, id_ruta, lista_estaciones, tiempos_viaje, es_circular=True):
        """
        :param lista_estaciones: Lista de IDs de estaciones o objetos Estacion.
        :param tiempos_viaje: Lista de tiempos (int) para llegar a la siguiente estación.
        :param es_circular: Booleano, si la ruta vuelve al inicio al terminar.
        """
        self.id = id_ruta
        self.estaciones = lista_estaciones 
        self.tiempos = tiempos_viaje 
        self.circular = es_circular 

    def obtener_siguiente_estacion(self, estacion_actual):
        """Dada una estación, retorna cuál es la siguiente en la línea."""
        try:
            # Buscamos el índice de la estación actual
            # Nota: Esto asume que estacion_actual es el objeto o ID guardado en la lista
            idx = self.estaciones.index(estacion_actual)
            
            # Si no es la última, devolvemos la siguiente
            if idx + 1 < len(self.estaciones):
                return self.estaciones[idx + 1]
            # Si es la última y la ruta es circular, volvemos a la primera
            elif self.circular:
                return self.estaciones[0]
        except ValueError:
            return None
        return None

    def __repr__(self):
        return f"Ruta({self.id}, paradas={len(self.estaciones)})"