import pickle

class SistemaGuardado:
    @staticmethod
    def guardar_estado(estado, ruta_archivo):
        """
        Guarda el objeto EstadoSimulacion completo en un archivo binario.
        Esto congela el tiempo, trenes, pasajeros y rutas.
        """
        try:
            with open(ruta_archivo, 'wb') as f:
                pickle.dump(estado, f)
            return True
        except Exception as e:
            print(f"Error al guardar: {e}")
            return False

    @staticmethod
    def cargar_estado(ruta_archivo):
        """
        Lee un archivo binario y recupera el objeto EstadoSimulacion.
        """
        try:
            with open(ruta_archivo, 'rb') as f:
                estado_recuperado = pickle.load(f)
            return estado_recuperado
        except Exception as e:
            print(f"Error al cargar: {e}")
            return None