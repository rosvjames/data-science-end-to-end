# Semana 11, Sesión 2: Esquemas de validación y evaluación de modelos

> Objetivo de la sesión: seleccionar un esquema de validación adecuado al contexto de los datos de tu proyecto (aleatorio, temporal, por grupo) y elegir la métrica de evaluación correcta según el costo relativo de cada tipo de error.

**Lectura previa de esta sesión:** ["How Metrics (and LLMs) Can Trick You: A Field Guide to Paradoxes"](https://towardsdatascience.com/how-metrics-and-llms-can-trick-you-a-field-guide-to-paradoxes/), Towards Data Science.

**Referencia de esta sesión:** *Designing Machine Learning Systems*, Chip Huyen, capítulo 6 (desarrollo y evaluación de modelos offline).

## Requisitos antes de esta sesión

Nada nuevo que instalar: todo lo de hoy está en scikit-learn. Ten a mano tu `pipeline_proyecto.py` y el modelo final que elegiste la sesión pasada. Los laboratorios de hoy son notebooks, como los de la Semana 10 y la sesión pasada.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué es la paradoja de la exactitud (accuracy paradox)? ¿Qué métricas recomienda en su lugar?**

La paradoja de la exactitud es que un modelo puede tener una accuracy muy alta y ser inútil cuando las clases están muy desbalanceadas: si solo 5% de los pagos son fraude, predecir siempre "no es fraude" acierta 95% sin detectar nada. En su lugar se usan métricas que miran cada clase por separado: precisión, recall, F1, la matriz de confusión o el área bajo la curva. _(Respuesta general: no pude abrir el artículo, que devolvió un error 403; compárala con lo que dice.)_

**El artículo cita la ley de Goodhart: "cuando una medida se convierte en objetivo, deja de ser una buena medida". ¿Qué ejemplo da, y qué tiene que ver con elegir un modelo por una sola métrica?**

_(tu respuesta)_

## Pregunta de apertura

La sesión pasada elegiste el modelo con menor error sobre los 595 viajes de prueba. ¿Cuánto cambiaría ese error si la división hubiera sido otra? ¿Lo viste en algún lado del registro?

Cambiaría bastante: con una sola división el gradient boosting dio 1.2754, pero la validación cruzada con 5 pliegues al azar dio pliegues entre 1.16 y 1.28 (promedio 1.2288), y con otra semilla en el registro de la sesión pasada dio 1.1867. Sí lo vi en el registro, en las dos corridas del gradient boosting con distinta `semilla_division`.

## Ejercicio 1: tres formas de validar el mismo modelo

Notebook: [`starter/ejercicio1_validacion.ipynb`](./starter/ejercicio1_validacion.ipynb), sobre [`starter/viajes_features.csv`](./starter/viajes_features.csv), con la preparación de [`starter/preparacion_taxis.py`](./starter/preparacion_taxis.py). Ya trae una función `evaluar` que corre una validación cruzada con el esquema que le pases y guarda el error de cada pliegue. Los 4 `TODO` son tres esquemas de validación y dos métricas. Córrelo completo una vez antes de tocar nada (**Run All**).

**Respuesta 1 (TODO 1):** con una sola división, el gradient boosting dio 1.2754 y el bosque 1.3016. Con 5 pliegues al azar, ¿esperas que los cinco errores del gradient boosting sean parecidos entre sí? ¿Cuánto esperas que varíen?

Esperaba que los cinco errores fueran parecidos, porque los pliegues son muestras al azar de los mismos datos, pero no idénticos: variaciones de unas pocas centésimas a una décima. Salieron 1.28, 1.24, 1.16, 1.24 y 1.23, con desviación de 0.036: el promedio (1.2288) es más confiable que el 1.2754 de una sola división, que cae en la parte alta del rango.

**Respuesta 2 (TODO 2):** en la validación temporal, cada pliegue entrena con los viajes anteriores y valida con los siguientes. ¿Esperas un error mayor o menor que con pliegues al azar? ¿Por qué?

Esperaba un error mayor, porque se entrena con el pasado y se valida con el futuro: no hay viajes "del mismo periodo" mezclados y el primer pliegue entrena con muy pocos viajes. Fue así: 1.3099 de promedio (pliegues 1.40, 1.21, 1.38, 1.27, 1.29) contra 1.2288 al azar, con más variación (desviación 0.069). Es la estimación más realista si la app va a predecir viajes futuros.

**Respuesta 3 (TODO 3):** en la validación por zona, ninguna zona de origen aparece a la vez en entrenamiento y en validación. ¿Qué pliegue crees que va a tener el peor error?

Esperaba que fuera el pliegue con JFK Airport, porque es la zona más distinta (tarifas fijas, viajes largos) y el modelo no la ve al entrenar. Así fue: el pliegue 5 (Brooklyn y JFK Airport) tuvo error 6.43, contra 1.19 a 1.31 de los demás. Ese pliegue tiene 31.5% de viajes de tarifa fija, contra 4% a 6% de los otros.

**Respuesta 4 (TODO 4):** la app muestra una tarifa estimada antes del viaje, y el pasajero reclama si la real sale más de 20% por encima. ¿Qué métrica dice mejor cuántos reclamos va a haber: el MAE, el RMSE, o el porcentaje de viajes subestimados en más de 20%?

El porcentaje de viajes subestimados en más de 20%, porque es exactamente el evento que genera el reclamo. El MAE (1.2754) y el RMSE (1.9213) promedian errores en las dos direcciones y no distinguen entre sobreestimar (no genera reclamo) y subestimar. En la prueba, 4.4% de los viajes quedaron subestimados en más de 20%.

**Lo que confirmó la tabla, esquema por esquema:**

| Esquema | Promedio MAE | Desviación | Peor pliegue |
|---|---|---|---|
| Al azar, gradient boosting | 1.2288 | 0.0361 | 1.28 |
| Al azar, bosque | 1.2887 | 0.0286 | 1.33 |
| Temporal, gradient boosting | 1.3099 | 0.0693 | 1.40 |
| Por zona, gradient boosting | 2.2996 | 2.0648 | 6.43 (Brooklyn y JFK) |

## Durante los ConcepTests

**ConcepTest 1. Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

**ConcepTest 2. Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

## Ejercicio 2: el 95% que no detecta nada

Solo o en pareja. Notebook: [`starter/ejercicio2_fraude_y_umbral.ipynb`](./starter/ejercicio2_fraude_y_umbral.ipynb), sobre [`starter/pagos_taxi.csv`](./starter/pagos_taxi.csv): 6000 pagos de la app de taxis, de los que unos 300 resultaron fraudulentos. Mismo esqueleto del Ejercicio 1, con un problema de clasificación. Los pasos 1 a 3 tienen `TODO`; los pasos 4 y 5 solo tienen la comprobación. Complétalos hasta que todas digan `OK`.

**Respuesta 1:** ¿qué accuracy tiene la línea base que nunca predice fraude? ¿Y qué recall?

Accuracy 0.9508 (95.1%) y recall 0.0: nunca predice fraude, así que acierta todos los pagos legítimos y no detecta ninguno de los fraudulentos.

**Respuesta 2:** ¿cuánto mejora la accuracy del gradient boosting sobre la línea base, y cuánto mejora el recall? ¿Cuál de los dos números describe mejor lo que gana la empresa?

La accuracy sube de 0.9508 a 0.9712 (unos 2 puntos) y el recall de 0 a 0.4610 (46 puntos). El recall describe mejor lo que gana la empresa: es la proporción de fraudes que se detectan; la accuracy casi no se mueve porque 95% de los pagos son legítimos.

**Respuesta 3:** con el umbral 0.5, ¿cuántos fraudes deja pasar el gradient boosting? ¿Qué umbral eligió el paso 5, y cuántos fraudes y falsas alarmas tiene con ese umbral?

Con el umbral 0.5 deja pasar 159 de los 295 fraudes (y solo 14 falsas alarmas). El paso 5 eligió el umbral 0.1: con él quedan 122 fraudes sin detectar y 222 falsas alarmas, con un costo total de 5546 dólares frente a 6402 con el umbral 0.5.

**Si terminas antes:** si la revisión manual de una falsa alarma costara 20 dólares en vez de 3, ¿el umbral elegido sube o baja? Cambia la constante y comprueba.

Sube: con 20 dólares por falsa alarma, el costo más bajo pasa al umbral 0.5 (6640 dólares, contra 7300 en 0.2 y 9320 en 0.1), porque cada falsa alarma cuesta casi lo mismo que la mitad de un fraude y ya no conviene marcar tantos pagos dudosos. Lo calculé con los fraudes no detectados y las falsas alarmas de cada umbral de la tabla (no cambié la constante del notebook).

## Ejercicio 3: la validación y la métrica de tu proyecto

Usa tu `pipeline_proyecto.py` y el modelo final de la sesión pasada. Esta vez no hay plantilla.

### Entregable 1: `validacion_proyecto.ipynb`

Un notebook, al lado de tu `pipeline_proyecto.py`, que evalúe tu modelo final (y el segundo mejor) con validación cruzada, con dos esquemas: el que corresponde a tus datos (temporal si predices el futuro, por grupo si la misma entidad aparece muchas veces, estratificado si clasificas una clase poco frecuente) y uno al azar, para comparar. El notebook guarda una tabla con el promedio, la desviación y cada pliegue.

### Entregable 2: la métrica del negocio

Escribe qué error es más caro en tu proyecto (sobreestimar o subestimar, un falso positivo o un falso negativo) y cuánto, aunque sea aproximado. Calcula en el mismo notebook una métrica que refleje ese costo, además de la métrica que venías usando.

### Entregable 3: respuestas

**¿Qué esquema de validación corresponde a tu proyecto, y por qué?**

El temporal. El modelo predice las ventas de mañana a partir del pasado, así que la validación tiene que entrenar con días anteriores y validar con días posteriores (`TimeSeriesSplit`, 5 pliegues). Con un esquema al azar, los días vecinos del mismo producto quedan repartidos entre entrenamiento y validación y el modelo "ve" el futuro durante el entrenamiento. Para que la validación cruzada fuera viable usé 150 productos al azar con sus últimos 730 días (107 386 filas). Notebook: `psets/proyecto/modelado/validacion_proyecto.ipynb`; tabla: `validacion_proyecto.csv`.

**¿Cambió la conclusión entre el esquema al azar y el tuyo? Muestra los números.**

No cambió la conclusión, pero sí la certeza. Gradient boosting: MAE 1.0138 ± 0.0249 (temporal) y 1.0192 ± 0.0091 (al azar). Red neuronal: 1.0672 ± 0.0430 (temporal) y 1.0410 ± 0.0132 (al azar). El gradient boosting gana en los dos esquemas; el esquema temporal da una variación entre pliegues unas 3 veces mayor y, para la red, un error mayor (1.067 contra 1.041), como se esperaría al validar con el futuro. El esquema al azar subestima la variación y hace ver mejor a la red.

**¿La diferencia entre tu modelo final y el segundo es mayor que la variación entre pliegues? ¿Sigues eligiendo el mismo?**

Sí, ahora sí. En la validación temporal, el gradient boosting (1.0138) le gana a la red (1.0672) por 0.053, más del doble de su desviación entre pliegues (0.025 y 0.043), y gana en los 5 pliegues (1.054 contra 1.120, 1.001 contra 1.063, 1.015 contra 1.108, 0.978 contra 1.004 y 1.020 contra 1.040). Con una sola división, la red parecía mejor por 0.018 (1.0713 contra 1.0895 de la Semana 11); la validación cruzada contradice esa diferencia, así que era ruido de esa división. Sigo eligiendo el gradient boosting, ahora con evidencia a favor y no solo por la explicabilidad. Aclaración: la validación usa un subconjunto (150 productos, 730 días) y los números no son comparables con los de la prueba completa.

**¿Qué métrica del negocio elegiste, y qué dice que no decía la anterior?**

Un costo asimétrico: 2 por cada unidad pronosticada de menos (venta perdida porque se agota el producto) y 1 por cada unidad de más (merma e inventario inmovilizado). Es un supuesto mío; los pesos reales dependen de los márgenes y la merma de cada producto. Dice lo que el MAE no dice: de qué lado se equivoca el modelo. En la validación temporal, la red tiene un MAE 5% mayor que el gradient boosting (1.067 contra 1.014), pero su costo es 10% mayor (1.678 contra 1.522): se equivoca más del lado caro, quedándose corta. Con el MAE solo, ese riesgo se subestima.

## Antes de la próxima sesión

**Lectura:** ["MLOps: Batch vs Online ML Systems"](https://medium.com/mlops-republic/mlops-batch-vs-online-ml-system-cbacee834837), MLOps Republic.

La app de taxis usa dos modelos: uno estima la tarifa antes de pedir el viaje, otro decide si un pago es fraude. ¿Alguno de los dos se podría calcular una vez por noche para todos los casos posibles? ¿Cuál tiene que responder en el momento, y en cuánto tiempo?

El de fraude tiene que responder en el momento del pago, antes de aprobar el cobro, en una fracción de segundo (menos de un segundo). La tarifa se podría calcular una vez por noche solo si dependiera de pocas combinaciones (zona de origen, zona de destino y hora: 8 × 8 × 24 = 1536 casos); como usa la distancia exacta y el número de pasajeros, no se puede enumerar y conviene responder en línea, aunque tolera unos segundos de espera. _(Razonamiento propio; no leí el artículo.)_
