class Pasajero:
    def __init__(self, id_pasajero, origen_id, destino_id, hora_creacion):
        self.id = id_pasajero
        self.origen = origen_id      # ID de la estación de origen
        self.destino = destino_id    # ID de la estación de destino
        self.hora_creacion = hora_creacion
        
        # Estados posibles: "ESPERANDO", "VIAJANDO", "COMPLETADO"
        self.estado = "ESPERANDO" 
        self.hora_llegada = None     # Se llenará cuando llegue a su destino

    def completar_viaje(self, hora_actual):
        self.estado = "COMPLETADO"
        self.hora_llegada = hora_actual

    def __repr__(self):
        return f"Pasajero({self.id}: {self.origen}->{self.destino})"