class Estacion:
    def __init__(self, nombre: str, poblacion: int, x=0, y=0):
        # El ID será el nombre (para simplificar)
        self.id = nombre 
        self.nombre = nombre
        self.poblacion = poblacion
        
        # Coordenadas para la interfaz gráfica (RF03)
        self.x = x
        self.y = y
        
        # Gestión de vías (RF01)
        self.vias = []
        self.flujo_acumulado = 0

    def __str__(self):
        return f"Estación {self.nombre} (Población: {self.poblacion})"
    