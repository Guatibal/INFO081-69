# main.py

# 1. Imports del Sistema
import tkinter as tk

# 2. Imports de Lógica y Modelos
from logica.estado_simulacion import EstadoSimulacion
from logica.gestor_datos import GestorDatos # <--- NUEVO: Para leer el JSON
from models.estacion import Estacion
from models.ruta import Ruta
from models.tren import Tren
from models.generador import GeneradorPasajeros

# 3. Imports de Interfaz Gráfica
from ui.ventana_principal import VentanaPrincipal
from ui.ventana_config import VentanaConfig 

def iniciar_simulacion_real():
    """
    Esta función se ejecuta al dar click en 'Iniciar Simulación' en el Launcher.
    Carga los datos desde el GestorDatos (JSON) y construye el mundo.
    """
    print("--- INICIANDO SIMULACIÓN ---")
    print("Cargando datos desde gestor...")
    
    # 1. Inicializar el estado y el gestor
    simulacion = EstadoSimulacion()
    gestor = GestorDatos() # Esto carga automáticamente el JSON si existe
    datos = gestor.obtener_datos()

    # --- PROTECCIÓN: SI NO HAY DATOS ---
    # Si el usuario no ha creado nada en el Admin, creamos datos por defecto
    if not datos["estaciones"]:
        print("⚠️ No hay configuración personalizada.")
        print("🔄 Cargando escenario de ejemplo: 'Ferroviario Valdivia' -> 'Ferroviario Bio-Bio'")
        
        # 1. Definimos las estaciones del ejemplo "dummy" pero con coordenadas visuales
        datos["estaciones"] = [
            {
                'id': 'Ferroviario Valdivia', 
                'nombre': 'Ferroviario Valdivia', 
                'vias': 2,     # Asumimos 2 vías como en el ejemplo
                'x': 200,      # Coordenada X para que se vea a la izquierda
                'y': 350       # Coordenada Y (centro vertical)
            },
            {
                'id': 'Ferroviario Bio-Bio', 
                'nombre': 'Ferroviario Bio-Bio', 
                'vias': 2, 
                'x': 600,      # Coordenada X para que se vea a la derecha
                'y': 350
            }
        ]
        
        # 2. Definimos el tren del ejemplo
        datos["trenes"] = [
            {
                'id': 'Tren-Dummy', 
                'capacidad': 80, 
                'velocidad': 12
            }
        ]
        
    # Diccionario temporal para guardar los objetos Estacion creados
    # Lo necesitamos para luego asignar las rutas y generadores
    mapa_estaciones_obj = {} 

    # --- 2. CREAR ESTACIONES ---
    print(f"Generando {len(datos['estaciones'])} estaciones...")
    for est_data in datos["estaciones"]:
        # Crear objeto Estacion
        nueva_estacion = Estacion(est_data['id'], 500, x=est_data['x'], y=est_data['y'])
        
        # Generar las VÍAS según el número configurado
        for i in range(est_data['vias']):
            nueva_estacion.vias.append(f"Via-{i+1}")
            
        simulacion.registrar_entidad(nueva_estacion)
        mapa_estaciones_obj[est_data['id']] = nueva_estacion

    # --- 3. CONFIGURAR GENERADORES DE PASAJEROS ---
    # Ahora que todas las estaciones existen, podemos decirles a dónde va la gente
    lista_todos_ids = list(mapa_estaciones_obj.keys())
    
    for id_est, estacion_obj in mapa_estaciones_obj.items():
        # Los destinos posibles son todas las estaciones MENOS la propia
        destinos_posibles = [uid for uid in lista_todos_ids if uid != id_est]
        
        # Asignar generador
        gen = GeneradorPasajeros(id_est, destinos_posibles)
        estacion_obj.asignar_generador(gen)

    # --- 4. CREAR RUTAS AUTOMÁTICAS ---
    # Como aún no administramos rutas complejas, crearemos una ruta única
    # que conecte todas las estaciones en el orden que fueron creadas.
    lista_objs_estaciones = list(mapa_estaciones_obj.values())
    
    # Solo creamos ruta si hay al menos 2 estaciones
    ruta_principal = None
    if len(lista_objs_estaciones) >= 2:
        # Calculamos tiempos (ej: 10 min entre cada una)
        tiempos = [10] * (len(lista_objs_estaciones) - 1)
        
        ruta_principal = Ruta("Ruta-General", lista_objs_estaciones, tiempos)
        simulacion.registrar_entidad(ruta_principal)
        print("Ruta automática creada conectando todas las estaciones.")

    # --- 5. CREAR TRENES ---
    print(f"Generando {len(datos['trenes'])} trenes...")
    for tren_data in datos["trenes"]:
        nuevo_tren = Tren(tren_data['id'], tren_data['capacidad'], tren_data['velocidad'])
        
        if ruta_principal:
            nuevo_tren.ruta_actual = ruta_principal
            nuevo_tren.estacion_actual = lista_objs_estaciones[0] # Empieza en la primera
        
        simulacion.registrar_entidad(nuevo_tren)

    # --- 6. LANZAR VENTANA PRINCIPAL ---
    app = VentanaPrincipal(simulacion)
    app.iniciar()

def main():
    # Iniciamos el Launcher
    # Le pasamos la función de arriba para que la ejecute cuando demos "Iniciar"
    launcher = VentanaConfig(callback_iniciar=iniciar_simulacion_real)
    launcher.mostrar()

if __name__ == "__main__":
    main()