El presente informe detalla el diseño para el proyecto de simulación de una red ferroviaria.
El propósito del sistema  es ofrecer una herramienta interactiva donde un usuario,
en el rol de "Operario", pueda modelar, ejecutar y monitorear el tráfico de trenes en una red definida.

El software se estructurará en varios componentes principales.
El primero es un módulo de gestión (CRUD) que permite al Operario definir los elementos base de la simulación:
Trenes, Estaciones y las Rutas que los conectan.

El segundo componente es el motor de simulación, que procesará el avance del sistema por turnos discretos,
permitiendo al Operario iniciar, pausar y reanudar la ejecución.

Finalmente, el diseño incluye un módulo de persistencia de datos; este utilizará archivos en formato CSV para 
guardar el estado actual de la simulación y permitir cargar partidas guardadas, además de leer una configuración 
inicial. El sistema también registrará una bitácora cronológica de todos los eventos relevantes (llegadas, salidas, 
etc.) para su consulta posterior por parte del Operario.

El proyecto se organiza en diferentes carpetas.
En la carpeta "models" se incluyen las clases que representan las entidades del sistema (trenes, estaciones y rutas).
En la carpeta "logic" se incuye la logica del simuulador, incluyendo la clase encargada del estado de la simulación.
En la carpeta "ui" se incluiran las ventanas correspondientes a la interfaz del usuario.
En la carpeta "config" se almacenarán configuraciones generales del programa, como colores y tamaños de ventana.

Para ello los integrantes del equipo de trabajo seran:
-Oscar Soto
-Sebastian Pohl
-Gabriel Rios
-Tomás Riquelme

## Cómo Ejecutar el Proyecto
1.  Asegúrate de tener Python 3 instalado.
2.  Clona el repositorio.
3.  Desde la carpeta raíz del proyecto, ejecuta el archivo principal en la terminal:

## indicadores
1. Tiempo de espera promedio
2. Total de pasajeros transportados hoy
