import datetime

class EstadoSimulacion:
    def __init__(self):
        self.hora_actual = None
        
        self.estaciones = {}
        self.trenes = {}
        self.rutas = {}

    def iniciar_desde_base(self):
        self.hora_actual = datetime.datetime(2015, 3, 1, 7, 0, 0)
        print(f"Simulación iniciada en: {self.hora_actual}")
