# Bitácora de trabajo - TPO Programación 1 - Grupo 9

## Entrega 1

Durante la primera entrega, el trabajo fue dividido entre los integrantes del grupo por módulos. Cada integrante también realizó las pruebas correspondientes a su módulo.

### Mateo
- Desarrollo del módulo `flota.py`.
- Implementación de las reglas de ubicación de las naves.
- Desarrollo de la ubicación manual y automática de la flota.
- Desarrollo de las pruebas en `test_flota.py`.

### Nico
- Desarrollo del módulo `radar.py`.
- Implementación de la búsqueda lineal de naves.
- Registro de la cantidad de comparaciones realizadas durante la búsqueda.
- Desarrollo de las pruebas en `test_radar.py`.

### Celina
- Desarrollo del módulo `registro.py`.
- Implementación del historial de eventos de la partida.
- Desarrollo de estadísticas y resumen de la partida.
- Desarrollo de las pruebas en `test_registro.py`.

### Thomas
- Desarrollo del módulo `tablero.py`.
- Creación y manejo del cubo tridimensional.
- Validación de coordenadas y acceso/modificación de celdas.
- Representación de los planos del cubo y estados de las celdas.
- Desarrollo de las operaciones básicas con matrices.
- Desarrollo de `test_tablero.py`.

- Desarrollo del módulo `armamento.py`.
- Creación del catálogo inicial de armamento.
- Implementación del funcionamiento del torpedo.
- Desarrollo de `test_armamento.py`.

- Desarrollo e integración del módulo `partida.py`.
- Implementación del menú principal y submenú de ubicación.
- Integración de los módulos de tablero y flota.
- Visualización del estado del tablero.
- Desarrollo de `test_partida.py`.

Integracion 1: Mateo, Nico, Celina, Thomas
Encargado de Subirlo 1: Thomas
- Integración de los módulos desarrollados en el grupo.
- Resolución de conflictos entre ramas.
- Corrección de errores encontrados durante la integración.
- Ejecución y verificación de las pruebas generales del proyecto.


## Entrega 2

A lo largo de la segunda entrega se cambiaron los modulos trabajados por cada integrante. Cada integrante también realizó las pruebas correspondientes a su nuevo módulo.

### Mateo
- Desarrollo del módulo `armamento.py`.
- Implementación de armas de área: racimo, carga de profundidad y barrido láser.
- Implementación del manejo de munición y del uso del torpedo sobre celdas detectadas por sonar.
- Desarrollo del registro de impactos y el estado de las naves en `flota.py`.
- Desarrollo de la obtención y representación de planos x e y, y de las celdas vecinas en `tablero.py`.
- Desarrollo de las pruebas en `test_armamento.py`, `test_flota.py` y `test_tablero.py`.

### Yamil
- Desarrollo del módulo `radar.py`.
- Implementación de la búsqueda optimizada mediante un índice hash reutilizable.
- Implementación del sonar por planos y la detección de naves.
- Desarrollo de las pruebas en `test_radar.py`.

### Celina
- Desarrollo e integración del módulo `partida.py`.
- Implementación de la configuración de partidas, los turnos, los disparos y las condiciones de victoria.
- Implementación de la ubicación manual y aleatoria de flotas, los modos de juego, los menús y el resumen final.
- Desarrollo de `errores.py` para manejar configuraciones y jugadas inválidas.
- Desarrollo de las pruebas en `test_partida.py`.

### Thomas
- Integración y corrección del módulo `partida.py`.
- Implementación del cierre de la partida al determinarse un ganador.
- Corrección de la detección de victoria cuando la flota rival está vacía.
- Desarrollo de las pruebas para el cierre de la partida y las condiciones de victoria en `test_partida.py`.
- Actualización de `.gitignore` para ignorar archivos de caché de Python.

Integración 2: Mateo, Yamil, Celina, Thomas
Encargado de subirlo 2: Mateo
- Integración de los módulos desarrollados en el grupo.
- Resolución de conflictos entre ramas.
- Corrección de errores encontrados durante la integración.
- Ejecución y verificación de las pruebas generales del proyecto.
