# main.py

# 1. Imports del Sistema
import tkinter as tk

# 2. Imports de Lógica y Modelos
from logica.estado_simulacion import EstadoSimulacion
from logica.gestor_datos import GestorDatos
from models.estacion import Estacion
from models.ruta import Ruta
from models.tren import Tren
from models.generador import GeneradorPasajeros
from models.grafo_rutas import GrafoRutas

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
    
    # 1. Inicializar el estado, el gestor y el grafo de rutas
    simulacion = EstadoSimulacion()
    gestor = GestorDatos()
    datos = gestor.obtener_datos()
    grafo = GrafoRutas()

    # --- PROTECCIÓN: SI NO HAY DATOS ---
    if not datos["estaciones"]:
        print("⚠️ No hay configuración personalizada.")
        print("🔄 Cargando escenario de ejemplo con 3 estaciones")
        
        datos["estaciones"] = [
            {
                'id': 'Ferroviario Valdivia', 
                'nombre': 'Ferroviario Valdivia', 
                'vias': 2,
                'x': 200,
                'y': 350
            },
            {
                'id': 'Estacion Temuco', 
                'nombre': 'Estación Temuco', 
                'vias': 2,
                'x': 400,
                'y': 450
            },
            {
                'id': 'Ferroviario Bio-Bio', 
                'nombre': 'Ferroviario Bio-Bio', 
                'vias': 2,
                'x': 600,
                'y': 350
            }
        ]
        
        datos["trenes"] = [
            {'id': 'Tren-1', 'capacidad': 80, 'velocidad': 12},
            {'id': 'Tren-2', 'capacidad': 100, 'velocidad': 15},
            {'id': 'Tren-3', 'capacidad': 60, 'velocidad': 10}
        ]

        # Rutas por defecto
        datos["rutas"] = [
            {'tren_id': 'Tren-1', 'origen': 'Ferroviario Valdivia', 'destino': 'Ferroviario Bio-Bio'},
            {'tren_id': 'Tren-2', 'origen': 'Estacion Temuco', 'destino': 'Ferroviario Valdivia'},
            {'tren_id': 'Tren-3', 'origen': 'Ferroviario Bio-Bio', 'destino': 'Estacion Temuco'}
        ]
    
    mapa_estaciones_obj = {}

    # --- 2. CREAR ESTACIONES ---
    print(f"Generando {len(datos['estaciones'])} estaciones...")
    for est_data in datos["estaciones"]:
        nueva_estacion = Estacion(est_data['id'], 500, x=est_data['x'], y=est_data['y'])
        
        # Generar las VÍAS según el número configurado
        for i in range(est_data['vias']):
            nueva_estacion.vias.append(f"Via-{i+1}")
            
        simulacion.registrar_entidad(nueva_estacion)
        mapa_estaciones_obj[est_data['id']] = nueva_estacion
        grafo.agregar_estacion(est_data['id'], nueva_estacion)

    # --- 3. CONFIGURAR CONEXIONES DEL GRAFO ---
    # Todas las estaciones están conectadas directamente
    lista_ids = list(mapa_estaciones_obj.keys())
    for i in range(len(lista_ids)):
        for j in range(i + 1, len(lista_ids)):
            id_a = lista_ids[i]
            id_b = lista_ids[j]
            est_a = mapa_estaciones_obj[id_a]
            est_b = mapa_estaciones_obj[id_b]
            
            # Calcular tiempo de viaje basado en distancia
            tiempo_viaje = grafo.calcular_tiempo_entre_estaciones(est_a, est_b)
            grafo.agregar_conexion(id_a, id_b, tiempo_viaje)
            print(f"  Riel conectado: {id_a} ↔ {id_b} ({tiempo_viaje} min)")

    # --- 4. CONFIGURAR GENERADORES DE PASAJEROS ---
    lista_todos_ids = list(mapa_estaciones_obj.keys())
    
    for id_est, estacion_obj in mapa_estaciones_obj.items():
        destinos_posibles = [uid for uid in lista_todos_ids if uid != id_est]
        gen = GeneradorPasajeros(id_est, destinos_posibles)
        estacion_obj.asignar_generador(gen)

    # --- 5. CREAR TRENES CON RUTAS ASIGNADAS DESDE CONFIG ---
    print(f"Generando {len(datos['trenes'])} trenes con rutas validadas...")
    rutas_creadas = {}
    config_rutas = {r['tren_id']: r for r in datos.get('rutas', [])}
    
    for idx, tren_data in enumerate(datos["trenes"]):
        nuevo_tren = Tren(tren_data['id'], tren_data['capacidad'], tren_data['velocidad'])
        
        # Obtener origen y destino de la configuración
        config = config_rutas.get(tren_data['id'], {})
        id_inicio = config.get('origen', lista_ids[idx % len(lista_ids)])
        id_fin = config.get('destino', lista_ids[(idx + 1) % len(lista_ids)])
        
        # VALIDAR que ambas estaciones existen
        if id_inicio not in mapa_estaciones_obj or id_fin not in mapa_estaciones_obj:
            print(f"⚠️  ERROR: Ruta inválida para {tren_data['id']}: {id_inicio} -> {id_fin}")
            id_inicio = lista_ids[0]
            id_fin = lista_ids[1] if len(lista_ids) > 1 else lista_ids[0]
        
        # Calcular el camino más corto usando Dijkstra
        try:
            camino_ids, tiempo_total = grafo.dijkstra(id_inicio, id_fin)
        except Exception as e:
            print(f"⚠️  ERROR al calcular ruta: {e}")
            continue
        
        # Convertir IDs a objetos Estacion
        camino_estaciones = [mapa_estaciones_obj[eid] for eid in camino_ids]
        
        # Calcular tiempos entre estaciones consecutivas
        tiempos = []
        for i in range(len(camino_ids) - 1):
            id_a = camino_ids[i]
            id_b = camino_ids[i + 1]
            tiempo = grafo.aristas[id_a][id_b]
            tiempos.append(tiempo)
        
        # Crear ruta calculada (no circular para rutas punto a punto)
        clave_ruta = f"{id_inicio}-{id_fin}"
        if clave_ruta not in rutas_creadas:
            ruta = Ruta(clave_ruta, camino_estaciones, tiempos, es_circular=False)
            simulacion.registrar_entidad(ruta)
            rutas_creadas[clave_ruta] = ruta
            print(f"  ✅ Ruta creada: {' → '.join(camino_ids)} ({tiempo_total} min total)")
        
        # Asignar ruta al tren
        nuevo_tren.ruta_actual = rutas_creadas[clave_ruta]
        nuevo_tren.estacion_actual = camino_estaciones[0]
        nuevo_tren.indice_estacion_actual = 0
        
        simulacion.registrar_entidad(nuevo_tren)
        print(f"  🚂 {tren_data['id']}: {id_inicio} → {id_fin}")

    # --- 6. LANZAR VENTANA PRINCIPAL ---
    app = VentanaPrincipal(simulacion)
    app.iniciar()

def main():
    launcher = VentanaConfig(callback_iniciar=iniciar_simulacion_real)
    launcher.mostrar()

if __name__ == "__main__":
    main()