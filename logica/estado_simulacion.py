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
        
        # --- HORARIO DE ALMUERZO ---
        self.hora_almuerzo_inicio = 13  # 13:00
        self.hora_almuerzo_fin = 14     # 14:00
        self.en_horario_almuerzo = False
        
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
        self.historial_logs = []

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

    def es_horario_almuerzo(self):
        """Retorna True si estamos entre las 13:00 y 14:00."""
        hora_actual = self.tiempo_actual.hour
        return self.hora_almuerzo_inicio <= hora_actual < self.hora_almuerzo_fin

    def avanzar_tiempo(self, segundos=60):
        hora_anterior = self.tiempo_actual.hour
        self.tiempo_actual += datetime.timedelta(seconds=segundos)
        hora_actual = self.tiempo_actual.hour
        
        # Detectar cambio de horario de almuerzo
        en_almuerzo_antes = self.hora_almuerzo_inicio <= hora_anterior < self.hora_almuerzo_fin
        en_almuerzo_ahora = self.es_horario_almuerzo()
        
        # Transición: COMIENZA hora de almuerzo
        if not en_almuerzo_antes and en_almuerzo_ahora:
            self.en_horario_almuerzo = True
            self.agregar_log("🍽️  HORA DE ALMUERZO - Todos los trenes se detienen en la próxima estación")
            # Marcar todos los trenes para detenerse
            for id_tren, tren in self.trenes.items():
                tren.debe_pausarse_por_almuerzo = True
        
        # Transición: TERMINA hora de almuerzo
        if en_almuerzo_antes and not en_almuerzo_ahora:
            self.en_horario_almuerzo = False
            self.agregar_log("✅ FIN DE ALMUERZO - Los trenes reanudan operaciones")
            # Reanudar todos los trenes
            for id_tren, tren in self.trenes.items():
                tren.pausado_por_almuerzo = False
        
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
        texto_completo = f"[{hora_str}] {mensaje}"
        
        # 1. Lo mandamos a la cola para que la UI lo muestre ahora
        self.logs_pendientes.append(texto_completo)
        
        # 2. Lo guardamos en el historial permanente (para el guardado de partida)
        self.historial_logs.append(texto_completo)

    def gestionar_parada_tren(self, tren):
        estacion = tren.obtener_estacion_actual()
        if not estacion: 
            return

        # 1. Bajar pasajeros
        bajan = tren.bajar_pasajeros_en_estacion(estacion.id)
        if bajan:
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
