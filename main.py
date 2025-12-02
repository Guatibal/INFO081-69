# 1. Imports
from logica.estado_simulacion import EstadoSimulacion
from models.estacion import Estacion
from models.ruta import Ruta
from models.tren import Tren
from models.generador import GeneradorPasajeros
from ui.ventana_principal import VentanaPrincipal
from ui.ventana_config import VentanaConfig # <--- Importamos el nuevo launcher

def iniciar_simulacion_real():
    """
    Esta función contiene toda la lógica de carga de datos (Hardcodeada por ahora).
    Se ejecutará SOLO cuando el usuario presione el botón en el Launcher.
    """
    print("Cargando simulación...")
    
    # --- 1. Inicializar el estado ---
    simulacion = EstadoSimulacion()

    # --- 2. Crear Estaciones ---
    est1 = Estacion("Central", 1000, x=100, y=300)
    est2 = Estacion("Norte", 500, x=400, y=100)
    est3 = Estacion("Sur", 500, x=400, y=500)

    simulacion.registrar_entidad(est1)
    simulacion.registrar_entidad(est2)
    simulacion.registrar_entidad(est3)

    # --- 3. Configurar Generadores ---
    gen_central = GeneradorPasajeros("Central", ["Norte", "Sur"])
    est1.asignar_generador(gen_central)
    
    gen_norte = GeneradorPasajeros("Norte", ["Sur"])
    est2.asignar_generador(gen_norte)
    
    gen_sur = GeneradorPasajeros("Sur", ["Central"])
    est3.asignar_generador(gen_sur)

    # --- 4. Crear Rutas y Trenes ---
    ruta1 = Ruta("R1", [est1, est2, est3], [10, 10])
    simulacion.registrar_entidad(ruta1)

    tren1 = Tren("T01")
    tren1.ruta_actual = ruta1
    tren1.estacion_actual = est1 
    simulacion.registrar_entidad(tren1)

    # --- 5. Iniciar la Interfaz Principal ---
    # Nota: Ya no usamos app.iniciar() porque el mainloop ya vendrá manejado
    # por la transición, pero creamos la ventana y la mantenemos viva.
    app = VentanaPrincipal(simulacion)
    app.iniciar()

def main():
    # En lugar de iniciar la simulación directo, iniciamos el Launcher.
    # Le pasamos la función 'iniciar_simulacion_real' como parámetro (callback).
    launcher = VentanaConfig(callback_iniciar=iniciar_simulacion_real)
    launcher.mostrar()

if __name__ == "__main__":
    main()