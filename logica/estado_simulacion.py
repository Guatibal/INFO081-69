import datetime
import copy
from collections import deque

class EstadoSimulacion:
    def __init__(self):
        # --- TIEMPO ---
        # Usaremos datetime para facilitar sumar minutos/segundos
        # Ejemplo: La simulación empieza a las 08:00:00
        self.tiempo_inicio = datetime.datetime(2023, 1, 1, 8, 0, 0)
        self.tiempo_actual = self.tiempo_inicio
        
        # --- ENTIDADES (RF01 y RF02) ---
        # Usamos diccionarios {id: Objeto} para búsquedas rápidas
        self.estaciones = {} 
        self.trenes = {}
        self.rutas = {}
        self.pasajeros = {} # RF02: Mantener personas existentes
        
        # --- EVENTOS (RF02) ---
        # Aquí guardaremos el historial de lo que pasó para el reporte final
        self.historial_eventos = [] 
        
        # Cola de eventos por procesar (Priority Queue sería ideal, pero una lista ordenada sirve)
        # Esto se conectará con el 'modulo-eventos' más adelante
        self.cola_eventos = [] 

        # Estado de ejecución
        self.ejecutando = False

    def registrar_entidad(self, entidad):
        """Método genérico para guardar estaciones, trenes o rutas."""
        # Detectamos el tipo de objeto y lo guardamos en su diccionario
        tipo = type(entidad).__name__
        
        if tipo == 'Estacion':
            self.estaciones[entidad.id] = entidad
        elif tipo == 'Tren':
            self.trenes[entidad.id] = entidad
        elif tipo == 'Ruta':
            self.rutas[entidad.id] = entidad
        elif tipo == 'Pasajero':
            self.pasajeros[entidad.id] = entidad

    def avanzar_tiempo(self, segundos=60):
        """Avanza el reloj y mueve las entidades."""
        self.tiempo_actual += datetime.timedelta(seconds=segundos)
        
        # Mover todos los trenes
        for id_tren, tren in self.trenes.items():
            tren.mover(segundos, self.tiempo_actual)

    def crear_snapshot(self):
        """
        CRUCIAL PARA RF09 (Lineas temporales/Multiverso).
        Devuelve una copia exacta e independiente del estado actual.
        """
        # copy.deepcopy crea duplicados de TODOS los objetos (trenes, rutas, etc.)
        # así, si modificas la copia, no afectas la simulación original.
        return copy.deepcopy(self)

    def reiniciar(self):
        """Vuelve la simulación al tiempo de inicio."""
        self.tiempo_actual = self.tiempo_inicio
        self.historial_eventos = []
        # Nota: Aquí habría que reiniciar posiciones de trenes también
        