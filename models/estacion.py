class Estacion:
    def __init__(self, nombre: str, poblacion: int):
        self.nombre = nombre
        self.poblacion = poblacion
        
        self.vias = []
        self.flujo_acumulado = 0

    def __str__(self):
        return f"Estación {self.nombre} (Población: {self.poblacion})"
