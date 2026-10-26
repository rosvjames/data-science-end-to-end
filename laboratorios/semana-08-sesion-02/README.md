# Semana 8, Sesión 2: Exploración y visualización de datos

> Objetivo de la sesión: explorar el dataset de tu proyecto con estadística descriptiva y visualizaciones para identificar patrones, outliers y supuestos que romperían un modelo antes de entrenarlo.

**Lectura previa de esta sesión:** ["A Data Scientist's Essential Guide to Exploratory Data Analysis"](https://towardsdatascience.com/a-data-scientists-essential-guide-to-exploratory-data-analysis-25637eee0cf6/), Towards Data Science.

**Referencia de esta sesión:** [Machine Learning Zoomcamp, Módulo 1 (DataTalksClub)](https://github.com/DataTalksClub/machine-learning-zoomcamp).

## Requisitos antes de esta sesión

pandas y matplotlib ya vienen en el Codespace. En tu laptop, instálalos con `pip install -r requirements.txt` desde la raíz del repositorio. Verifica con:

```
python3 -c "import matplotlib; print(matplotlib.__version__)"
```

Los scripts de hoy guardan cada gráfico como imagen en una carpeta `figuras/`. Ábrelas desde el explorador de archivos de VS Code. También puedes correr el mismo código en un notebook de Jupyter (en el Codespace, crea un archivo `.ipynb` y elige el kernel de Python 3.11), donde el gráfico aparece debajo de la celda.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué preguntas responde la exploración de datos antes de entrenar cualquier modelo?**

Qué contienen los datos (filas, columnas, tipos), qué falta o está duplicado, cómo se distribuye cada variable, qué valores son atípicos o imposibles y cómo se relacionan las variables entre sí y con el objetivo.

**El artículo distingue la exploración de una sola variable de la exploración de la relación entre dos. ¿Qué herramienta propone para cada una?**

Una variable: estadística descriptiva, histograma y boxplot. Dos variables: diagrama de dispersión y matriz de correlación.

## Pregunta de apertura

Entrenas un modelo que predice la tarifa de un viaje en taxi. Sin que lo sepas, 15 de los 3000 viajes tienen una tarifa de 999.99 por un error de captura. ¿Qué le pasa al modelo? ¿Lo notarías mirando solo su resultado final?

El modelo se sesga: 15 valores de 999.99 suben la media de la tarifa de ~26 a 31.4 y la desviación estándar a 71, y un modelo que minimiza el error cuadrático intenta acercarse a esos puntos y empeora con los viajes normales. Mirando solo el resultado final no se nota: verías un error alto sin saber por qué. Se detecta antes, en `describe()` o en un histograma.

## Ejercicio 1: resumen, distribución y atípicos

Archivo: [`starter/ejercicio1_explorar.py`](./starter/ejercicio1_explorar.py), sobre [`starter/viajes_taxi.csv`](./starter/viajes_taxi.csv): 3000 viajes en taxi de Nueva York, con fecha y hora de inicio, zona de origen y de destino, distancia, duración, pasajeros, método de pago, tarifa y propina. El script ya lee el archivo, arma los gráficos y los guarda en `figuras/`; faltan 4 `TODO`. Córrelo una vez antes de tocar nada:

```
cd laboratorios/semana-08-sesion-02/starter
python3 ejercicio1_explorar.py
```

**Respuesta 1 (TODO 1), antes de ver la solución:** en `describe()`, ¿qué dos valores de la tabla te harían sospechar de un error sin necesidad de graficar nada?

El máximo de `tarifa` (999.99, cuando el percentil 75 es 32.55) y el mínimo de `duracion_min` (-74, una duración negativa es imposible).

**Respuesta 2 (TODO 2):** abre `figuras/hist_tarifa.png` después del TODO 2. ¿Por qué casi todo el histograma queda comprimido a la izquierda?

_(tu respuesta)_

**Respuesta 3 (TODO 3 y 4):** la regla del IQR marca más de 300 viajes con tarifa atípica. ¿Esperas que todos sean errores? ¿Cómo lo averiguarías?

No. El IQR solo dice que un valor es raro, no que sea falso. Lo averiguaría agrupando los atípicos: contando sus tarifas repetidas (`value_counts()`) y sus zonas de origen y destino. Así se ve si siguen un patrón real o son valores imposibles.

**Lo que confirmó la salida, TODO por TODO:**

- 3000 filas y 10 columnas, sin duplicados. Faltan 120 valores de `pasajeros` y 60 de `metodo_pago`.
- IQR de la tarifa: límites [-13.85, 60.40] y 334 atípicos.
  - 15 son errores de captura (`tarifa == 999.99`).
  - 319 son reales: todos son viajes desde o hacia JFK Airport, 302 de ellos con la tarifa fija de 70.00.
- Otros valores imposibles: 10 viajes con duración negativa y 25 con distancia 0.
- Solo se quitan los 999.99 (quedan 2985 filas). La dispersión distancia–tarifa muestra una relación lineal hasta ~20 km, una meseta en 70 USD (JFK) y una columna de viajes con distancia 0 y tarifas de hasta 70.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: relaciones entre variables

Solo o en pareja. Archivo: [`starter/ejercicio2_relaciones.py`](./starter/ejercicio2_relaciones.py), sobre el mismo `viajes_taxi.csv`. Quita solo los errores que el Ejercicio 1 ya confirmó y completa los 5 `TODO`: dispersión de distancia contra tarifa, propina por método de pago, correlaciones con la tarifa, y pasajeros vacíos o en 0. Al final, el script imprime una comprobación por TODO: completa los 5 hasta que todas digan `OK`.

```
python3 ejercicio2_relaciones.py
```

**Hallazgo 1: qué muestra el gráfico de distancia contra tarifa, además de la tendencia general.**

Dos grupos que no siguen la recta. Hay 300 viajes con tarifa fija de 70.00, todos desde o hacia JFK Airport, sin importar la distancia (de ~13 a 45 km). También hay 25 viajes con distancia 0 que cobran entre 7.23 y 70: son errores de registro del GPS o del taxímetro.

**Hallazgo 2: qué pasa con la propina según el método de pago, y si crees que describe a los pasajeros o al sistema que registra los datos.**

Los 888 viajes en efectivo tienen propina 0 y los 2027 con tarjeta tienen una propina promedio de 4.73 (ninguno con 0). Describe al sistema, no a los pasajeros: la propina en efectivo no se registra. Usar `propina` como variable haría que el modelo aprenda el método de pago, no el comportamiento.

**Hallazgo 3: la duración tiene una correlación con la tarifa tan alta como la distancia. Si el modelo tiene que estimar la tarifa en el momento en que alguien pide el taxi, ¿puede usar la duración?**

No. La duración (correlación 0.956, casi igual a la de la distancia, 0.960) solo se conoce al terminar el viaje. Usarla es fuga de información (*data leakage*): el modelo se ve bien en las pruebas y falla en producción. Lo mismo pasa con `propina` (0.63).

## Ejercicio 3: explora el dataset de tu proyecto

Usa el archivo que tu pipeline de la Semana 7 deja listo para modelar, y la plantilla [`plantilla-eda/explorar_proyecto.py`](./plantilla-eda/explorar_proyecto.py).

### Paso 1: resumen y variable objetivo (5 minutos)

Reemplaza la ruta del archivo y el nombre de la columna que tu modelo va a predecir. Corre los pasos 1 a 3.

Archivo: `OBT.OBT_SALES` del pipeline M5 (Walmart), exportada de Snowflake (59.181.090 filas, sin llaves repetidas) y filtrada a la tienda CA_1 para que quepa en pandas: `plantilla-eda/obt_sales_CA_1.csv.gz` (no se sube al repo). Objetivo: `units`.

- 5.918.109 filas y 40 columnas (3049 items × 1941 días).
- Faltantes: `sell_price` y `revenue` 1.129.842 (las filas pre-lanzamiento); `date_key_ly_364` 1.109.836 (el primer año no tiene año anterior); `event_name_1` 5.436.367 y `event_name_2` 5.905.913 (son días sin evento, un nulo legítimo).
- `units`: mediana 0, Q3 1, máximo 648. El IQR marca 839.509 atípicos (14.2 %): todo valor ≥ 3. Con Q1 = 0 y Q3 = 1 la regla no sirve; solo refleja que el objetivo es asimétrico.

### Paso 2: relaciones (10 minutos)

Completa los pasos 4 y 5: la relación entre tu objetivo y la variable que esperas que más influya, y las consultas que confirman lo que encuentres.

Promedio de `units` por departamento (`figuras/objetivo_por_departamento.png`). FOODS_3 vende 2.50 unidades por día y item, 12 veces más que HOBBIES_2 (0.20). El departamento define el nivel de la serie, así que el modelo necesita `dept_id` (o el propio `item_id`). Las variables de calendario casi no se relacionan linealmente con `units`: `is_weekend` 0.06, `is_snap` 0.02, `is_event_day` -0.01.

### Paso 3: tres hallazgos que afectarían el modelado (10 minutos)

Para cada hallazgo, escribe qué encontraste, el número o el gráfico que lo confirma, y qué cambia en el modelo por su causa (una fila que quitas, una columna que no puedes usar, una variable que hay que transformar).

**Hallazgo 1:**

El 19.1 % de las filas (1.129.842) son días antes de que el item se lanzara: `units` siempre es 0 y `sell_price` es nulo. Son ceros falsos: suben los ceros de 55.2 % a 63.8 %. **Cambio:** quitar las filas con `is_pre_launch` antes de entrenar.

**Hallazgo 2:**

No todo cero es falta de demanda. De los ceros que quedan tras quitar el pre-lanzamiento, el 26.5 % está marcado como posible quiebre de stock (`is_suspected_stockout_nb`; 9.5 % con el criterio conservador), y los 12.642 registros de Navidad (`is_christmas_closed`) tienen 0 porque la tienda cierra. **Cambio:** excluir la Navidad y quitar o ponderar a la baja los quiebres de stock, para que el modelo no aprenda a predecir 0 cuando lo que faltó fue producto. Además el objetivo es de conteo y está sesgado (mediana 0, máximo 648), así que conviene una pérdida Poisson/Tweedie o `log1p(units)` en vez de error cuadrático sobre `units`.

**Hallazgo 3:**

`revenue` es exactamente `units × sell_price` (se cumple en el 100 % de las filas con precio) y tiene correlación 0.73 con el objetivo. Es fuga de información: no se conoce antes de vender. `_loaded_at` y `week_idx` son columnas de linaje del pipeline, no del negocio. **Cambio:** quitar `revenue`, `_loaded_at` y `week_idx` de las variables de entrada; `sell_price` sí se puede usar, porque se fija antes de la venta.

## Antes de la próxima sesión

**Lectura:** ["Feature Engineering that Makes Business Sense"](https://towardsdatascience.com/feature-engineering-that-makes-business-sense-419b9403236e/), Towards Data Science.

La tarifa fija de JFK y la hora del día no existen como columnas del dataset de taxis. ¿Cómo le darías esa información a un modelo?

Creando columnas nuevas a partir de las que existen. Para JFK, una variable `es_jfk` (1 si `zona_origen` o `zona_destino` es JFK Airport), que le dice al modelo que ahí la tarifa es fija y no depende de la distancia. Para la hora, extraer `hora` (y el día de la semana) de `fecha_hora_inicio`.
