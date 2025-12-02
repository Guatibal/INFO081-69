# Asegúrate de importar esto arriba si es necesario, 
# pero como lo inyectaremos, a veces no hace falta import.
# Para evitar líos de import circular, lo manejaremos dinámicamente.

class Estacion:
    def __init__(self, nombre: str, poblacion: int, x=0, y=0):
        self.id = nombre 
        self.nombre = nombre
        self.poblacion = poblacion
        self.x = x
        self.y = y
        
        self.vias = []
        self.andenes = [] # Pasajeros esperando
        self.flujo_acumulado = 0
        
        # El generador se asignará después
        self.generador = None

    def asignar_generador(self, generador):
        self.generador = generador

    def actualizar(self, tiempo_actual):
        """
        Se llama en cada tick de la simulación.
        Aquí la estación 'produce' pasajeros.
        """
        if self.generador:
            nuevos_pasajeros = self.generador.generar(tiempo_actual)
            if nuevos_pasajeros:
                for p in nuevos_pasajeros:
                    self.andenes.append(p)
                    print(f"[{tiempo_actual}] Nuevo pasajero en {self.nombre}: {p}")

    def __str__(self):
        return f"Estación {self.nombre} (Esperando: {len(self.andenes)})"