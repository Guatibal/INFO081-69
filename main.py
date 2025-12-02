from logica.estado_simulacion import EstadoSimulacion
from models.estacion import Estacion
from models.ruta import Ruta
from models.tren import Tren
from ui.ventana_principal import VentanaPrincipal

def main():
    # 1. Inicializar el estado
    simulacion = EstadoSimulacion()

    # 2. Cargar datos de prueba (Para verificar que se dibuja)
    # Creamos 3 estaciones con coordenadas
    est1 = Estacion("Central", 1000, x=100, y=300)
    est2 = Estacion("Norte", 500, x=400, y=100)
    est3 = Estacion("Sur", 500, x=400, y=500)

    simulacion.registrar_entidad(est1)
    simulacion.registrar_entidad(est2)
    simulacion.registrar_entidad(est3)

    # Creamos una ruta que las une: Central -> Norte -> Sur
    ruta1 = Ruta("R1", [est1, est2, est3], [10, 10])
    simulacion.registrar_entidad(ruta1)

    # Creamos un tren en esa ruta
    tren1 = Tren("T01")
    tren1.ruta_actual = ruta1
    # Truco temporal para que se dibuje: le decimos que está en la Estacion Central
    tren1.estacion_actual = est1 
    simulacion.registrar_entidad(tren1)

    # 3. Iniciar la interfaz gráfica
    app = VentanaPrincipal(simulacion)
    app.iniciar()

if __name__ == "__main__":
    main()