# TPO - Programación 1 - Grupo 9

Operación Cubo es un juego de batalla naval en un tablero tridimensional de 8 × 8 × 8. Permite ubicar flotas, jugar entre dos personas o contra la computadora, usar armas especiales, guardar partidas y consultar estadísticas.

## Requisitos

- Python 3.8 o posterior.
- Para ejecutar el juego no se necesitan paquetes externos.
- Para correr las pruebas, instalar `pytest`:

```bash
python -m pip install pytest
```

## Ejecutar

Desde la carpeta del proyecto:

```bash
python partida.py
```

El menú principal permite iniciar una partida entre dos personas, jugar contra la computadora con dificultad fácil o difícil, observar una partida entre dos máquinas, continuar una partida guardada y consultar el registro, la exportación CSV y el ranking.

Durante un turno se puede disparar, consultar los cubos, recorrer el cubo con cualquiera de los tres algoritmos disponibles o guardar y salir. Las armas disponibles son torpedo, misil de racimo, carga de profundidad, sonar, barrido láser, onda expansiva y torpedo guiado. El programa solicita los parámetros específicos de cada arma.

Las partidas y sus resultados se guardan en `datos/partidas/`. La opción de exportación crea un archivo CSV en la ruta indicada.

## Pruebas

```bash
python -m pytest -q
```

Los módulos de lógica se prueban por separado y también a través de las pruebas de integración de `partida.py` y `registro.py`.
