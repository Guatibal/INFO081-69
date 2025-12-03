import json
import os

class GestorDatos:
    _instancia = None
    ARCHIVO_CONFIG = "config_simulacion.json" # Aquí se guardará tu diseño

    def __new__(cls):
        # Patrón Singleton
        if cls._instancia is None:
            cls._instancia = super(GestorDatos, cls).__new__(cls)
            # Estructura base
            cls._instancia.datos = {
                "estaciones": [],
                "trenes": [],
                "rutas": []
            }
            # Intentamos cargar datos previos si existen
            cls._instancia.cargar_configuracion()
        return cls._instancia

    def obtener_datos(self):
        return self.datos

    # --- AGREGAR DATOS (Admin) ---
    def agregar_estacion(self, id_est, nombre, vias, x, y):
        # Evitar duplicados
        for e in self.datos["estaciones"]:
            if e["id"] == id_est:
                return False
        
        self.datos["estaciones"].append({
            "id": id_est,
            "nombre": nombre,
            "vias": int(vias),
            "x": int(x),
            "y": int(y)
        })
        self.guardar_configuracion() # Guardar automáticamente al agregar
        return True

    def agregar_tren(self, id_tren, capacidad, velocidad):
        # Evitar duplicados
        for t in self.datos["trenes"]:
            if t["id"] == id_tren:
                return False
                
        self.datos["trenes"].append({
            "id": id_tren,
            "capacidad": int(capacidad),
            "velocidad": int(velocidad)
        })
        self.guardar_configuracion()
        return True

    # --- PERSISTENCIA (JSON) ---
    def guardar_configuracion(self):
        """Guarda el diseño actual en un archivo de texto JSON"""
        try:
            with open(self.ARCHIVO_CONFIG, 'w') as f:
                json.dump(self.datos, f, indent=4)
            print(f"Configuración guardada en {self.ARCHIVO_CONFIG}")
        except Exception as e:
            print(f"Error al guardar config: {e}")

    def cargar_configuracion(self):
        """Carga el diseño previo si existe el archivo"""
        if os.path.exists(self.ARCHIVO_CONFIG):
            try:
                with open(self.ARCHIVO_CONFIG, 'r') as f:
                    self.datos = json.load(f)
                print("Configuración cargada exitosamente.")
            except Exception as e:
                print(f"Error al cargar config: {e}")
                
    def borrar_configuracion(self):
        """Elimina el archivo JSON y limpia la memoria."""
        # 1. Borrar archivo físico
        if os.path.exists(self.ARCHIVO_CONFIG):
            os.remove(self.ARCHIVO_CONFIG)
            print(f"Archivo {self.ARCHIVO_CONFIG} eliminado.")
        
        # 2. Limpiar memoria RAM
        self.datos = {
            "estaciones": [],
            "trenes": [],
            "rutas": []
        }
        return True