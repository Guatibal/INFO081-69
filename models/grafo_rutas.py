import heapq
import math

class GrafoRutas:
    """Gestiona las rutas entre estaciones usando un grafo y algoritmo de camino más corto (Dijkstra)."""
    
    def __init__(self):
        self.aristas = {}  # {id_est: {vecino_id: tiempo_viaje}}
        self.estaciones = {}  # {id_est: objeto_estacion}
    
    def agregar_estacion(self, id_estacion, obj_estacion):
        """Agrega una estación al grafo."""
        self.estaciones[id_estacion] = obj_estacion
        if id_estacion not in self.aristas:
            self.aristas[id_estacion] = {}
    
    def agregar_conexion(self, id_est_a, id_est_b, tiempo_viaje):
        """Agrega una conexión bidireccional entre estaciones."""
        if id_est_a not in self.aristas:
            self.aristas[id_est_a] = {}
        if id_est_b not in self.aristas:
            self.aristas[id_est_b] = {}
        
        self.aristas[id_est_a][id_est_b] = tiempo_viaje
        self.aristas[id_est_b][id_est_a] = tiempo_viaje
    
    def calcular_tiempo_entre_estaciones(self, est_a, est_b):
        """Calcula el tiempo de viaje basado en la distancia euclidiana."""
        distancia = math.sqrt((est_a.x - est_b.x)**2 + (est_a.y - est_b.y)**2)
        # Escala: 1 unidad de distancia = 1 minuto de viaje (ajusta según necesites)
        tiempo_viaje = max(5, int(distancia / 50))
        return tiempo_viaje
    
    def dijkstra(self, id_inicio, id_fin):
        """
        Calcula el camino más rápido entre dos estaciones usando Dijkstra.
        Retorna: (lista_ids_estaciones, tiempo_total)
        """
        # Inicializar distancias
        distancias = {est_id: float('inf') for est_id in self.estaciones.keys()}
        distancias[id_inicio] = 0
        padres = {est_id: None for est_id in self.estaciones.keys()}
        
        # Priority queue: (distancia, estacion_id)
        cola = [(0, id_inicio)]
        visitados = set()
        
        while cola:
            dist_actual, est_actual = heapq.heappop(cola)
            
            if est_actual in visitados:
                continue
            visitados.add(est_actual)
            
            # Si llegamos al destino, podemos parar
            if est_actual == id_fin:
                break
            
            # Explorar vecinos
            if est_actual in self.aristas:
                for vecino_id, tiempo in self.aristas[est_actual].items():
                    if vecino_id not in visitados:
                        nueva_dist = distancias[est_actual] + tiempo
                        
                        if nueva_dist < distancias[vecino_id]:
                            distancias[vecino_id] = nueva_dist
                            padres[vecino_id] = est_actual
                            heapq.heappush(cola, (nueva_dist, vecino_id))
        
        # Reconstruir camino
        camino = []
        actual = id_fin
        while actual is not None:
            camino.append(actual)
            actual = padres[actual]
        camino.reverse()
        
        tiempo_total = distancias[id_fin]
        
        return camino, tiempo_total