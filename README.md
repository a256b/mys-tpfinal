# Trabajo Práctico Final - Modelos y Simulación
## Enunciado
Una fábrica textil funciona de manera continua durante todos los días desde las 5am hasta las 8pm. Tiene una flota de 15 camiones que transportan diariamente materia prima y/o producto terminado. La fábrica cuenta con una planta de producción y una barraca de acopio de lana, situados a 5 km de distancia entre sí. Los camiones transportan la materia prima desde la barraca a la planta, siendo pesados en ambos lugares por balanzas especiales.

Para funcionar correctamente, la planta de producción requiere materia prima de manera constante. Cada 16 minutos, siguiendo una distribución Exponencial, un nuevo camión con carga arriba a la planta.

Una vez allí, cada camión es pesado en una balanza demorando un promedio de 11 min (+/-3) siguiendo una distribución Normal. Se estima que los valores de pesaje se comportan según el tipo de camión como los expresados en la **Tabla 2**. Luego, los camiones se descargan siguiendo los parámetros de la **Tabla 3**.

Cada ciclo de producción requiere al menos 1 tonelada de materia prima para poder realizarse y toma un promedio de 15 minutos, siguiendo una distribución Exponencial.

El producto terminado es cargado en camiones (**Tabla 3**) que deben volver a ser pesados por las balanzas y finalmente es despachado al centro de distribución. Este proceso demora en promedio lo establecido por la **Tabla 4**.

Al mismo tiempo, la barraca de la empresa tiene una capacidad máxima de 20000 toneladas de materia prima. Se considera necesaria la reposición de stock cuando este no supere las 8000 toneladas. Siendo así, el proceso de reposición es realizado por los camiones de carga al comenzar el día o al regresar del centro de distribución luego de haber despachado el producto terminado. Los camiones completarán su peso máximo para abastecer la barraca (ver **Tabla 1**).

Los dueños de la fábrica desean determinar la mejor estrategia para aumentar el uso de las balanzas y conocer cuánto se podría aumentar la producción. Se sabe que si las balanzas se encuentran ociosas en ciertos momentos del día, esto podría formar colas de camiones que llegan con materia prima y camiones que salen con producto terminado retrasando el funcionamiento y disminuyendo la producción general de la fábrica.

Consideraciones:
- Un año consta de 300 días.
- Los camiones se generan utilizando los datos de la **Tabla 1**.
- Los tiempos de atención de los operarios no se tienen en cuenta.
- Pese a las distancias entre sitios, no se tienen en cuenta las velocidades de viaje de los camiones. Utilizar las tablas para calcular tiempos de llegada.
- Si al momento de pesaje, el valor de balanza generado supera el peso máximo del tipo de vehículo siendo pesado, se tomará dicho peso máximo como valor final.

## Tablas
**Tabla 1 - Peso de los camiones**
|Tipo   |Peso s/c*   |Peso máx.   |Probabilidad   |Probabilidad acumulada   |
|---|---|---|---|---|
|1   |31   |38   |0.3   |0 <= x < 0.3   |
|2   |25   |30   |0.25   |0.3 <= x < 0.55   |
|3   |37   |44   |0.3   |0.55 <= x < 0.85   |
|4   |43   |52   |0.15   |0.85 <= x <= 1   |

*Peso s/c: sin carga (toneladas)

**Tabla 2 - Pesajes según tipo de camión (toneladas)**
|Tipo de camión  |Media   |Desvío   |
|---|---|---|
|1   |34   |6.2   |
|2   |27.5   |4.5   |
|3   |40   |2.3   |
|4   |49   |1.4   |

**Tabla 3 - Tiempo promedio de carga/descarga según tipo de camión (minutos)**
|Tipo  |Tiempo de carga/descarga   |
|---|---|
|1   |23   |
|2   |20   |
|3   |28   |
|4   |35   |

**Tabla 4 - Tiempos de viaje al centro de distribución (minutos)**
|Tipo de camión  |Media   |Desvío   |Demora por reabastecimiento   |
|---|---|---|---|
|1   |29   |5.1   |Ver tiempo de carga en **Tabla 3**   |
|2   |30   |6.4   |Ver tiempo de carga en **Tabla 3**   |
|3   |35   |8   |Ver tiempo de carga en **Tabla 3**   |
|4   |38   |12.3   |Ver tiempo de carga en **Tabla 3**   |

Los tiempos de esta tabla contemplan ida y vuelta
