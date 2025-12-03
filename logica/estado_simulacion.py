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

        self.logs_pendientes = []

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
        self.tiempo_actual += datetime.timedelta(seconds=segundos)
        
        # 1. Actualizar Estaciones (Generar pasajeros)
        for id_est, estacion in self.estaciones.items():
            estacion.actualizar(self.tiempo_actual)

        # 2. Mover Trenes y Gestionar Paradas
        for id_tren, tren in self.trenes.items():
            tren.mover(segundos, self.tiempo_actual)
            
            # Si el tren está en una estación (sea porque acaba de llegar o sigue ahí)
            if tren.en_estacion:
                self.gestionar_parada_tren(tren)
            
    def agregar_log(self, mensaje):
        """Guarda un mensaje con la hora actual para la interfaz."""
        hora_str = self.tiempo_actual.strftime("%H:%M")
        self.logs_pendientes.append(f"[{hora_str}] {mensaje}")

    def gestionar_parada_tren(self, tren):
        estacion = tren.obtener_estacion_actual()
        if not estacion: return

        # 1. Bajar pasajeros
        bajan = tren.bajar_pasajeros_en_estacion(estacion.id)
        if bajan:
            # En vez de print, usamos agregar_log
            self.agregar_log(f"Tren {tren.id} llegó a {estacion.nombre}: Bajaron {len(bajan)}.")
            
        for p in bajan:
            p.completar_viaje(self.tiempo_actual)

        # 2. Subir pasajeros
        suben = []
        for p in list(estacion.andenes):
            if tren.subir_pasajero(p):
                estacion.andenes.remove(p)
                p.estado = "VIAJANDO"
                suben.append(p)
        
        if suben:
            self.agregar_log(f"Tren {tren.id} en {estacion.nombre}: Subieron {len(suben)}.")
        
        # Si no subió ni bajó nadie, igual avisamos que llegó
        if not bajan and not suben:
             self.agregar_log(f"Tren {tren.id} pasó por {estacion.nombre} (Sin cambios).")

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
        