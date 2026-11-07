# Semana 10, Sesión 2: Entrenamiento y comparación de modelos II: ¿ensamblaje, red neuronal simple o un LLM?

> Objetivo de la sesión: comparar, sobre el problema de tu proyecto, un modelo de ensamblaje, una red neuronal simple entrenada con una librería de alto nivel y un LLM usado vía prompting, y decidir cuál conviene según desempeño, costo y explicabilidad.

**Lectura previa de esta sesión:** ["Machine Learning vs LLM: Differences, Applications & Impact"](https://www.neuralconcept.com/post/ml-vs-llm-key-differences-applications-engineering-impact), Neural Concept.

**Referencia de esta sesión:** [Neural network models, supervised (documentación oficial de scikit-learn)](https://scikit-learn.org/stable/modules/neural_networks_supervised.html).

## Requisitos antes de esta sesión

- Nada nuevo que instalar: la red neuronal es `MLPRegressor`, de scikit-learn.
- Acceso a un LLM de chat (ChatGPT, Claude, Gemini u otro; la versión gratuita alcanza), para el Ejercicio 2.
- La tabla de resultados de tu proyecto de la sesión pasada, y tu `pipeline_proyecto.py`.

Como la sesión pasada, los laboratorios son notebooks que importan la preparación de un script (`preparacion_taxis.py` en los Ejercicios 1 y 2, tu `pipeline_proyecto.py` en el 3).

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿para qué tipo de datos y de problema conviene el aprendizaje automático clásico, y para cuál un LLM?**

El aprendizaje automático clásico conviene con datos estructurados (tabulares) o conjuntos pequeños, y en problemas de clasificación, regresión, previsión o detección de anomalías (fraude, riesgo, mantenimiento predictivo), sobre todo si la latencia importa o se necesita interpretabilidad. Un LLM conviene con datos no estructurados, sobre todo texto: generación, resúmenes, chatbots, análisis de documentos y razonamiento semántico.

**El artículo compara las dos opciones en datos, costo y explicabilidad. ¿Cuál de esas tres diferencias pesa más para tu proyecto?**

La explicabilidad y el costo. Mi proyecto predice unidades vendidas por producto, tienda y día (tabla estructurada de millones de filas): un modelo clásico entrena en hardware normal y se puede auditar por qué sube o baja una predicción, mientras que un LLM sería un caja negra cobrada por consulta, y por cada producto y día habría que hacer una consulta. La diferencia de datos pesa menos porque tengo muchos datos tabulares.

## Pregunta de apertura

Para estimar la tarifa de un viaje, podrías entrenar un ensamblaje, entrenar una red neuronal o escribirle a un LLM los datos del viaje y pedirle un número. ¿Qué tendrías que medir de cada opción, además del error, para decidir cuál usar en la app de taxis?

Además del error: (1) el costo de entrenar y de cada predicción, (2) la latencia, porque la app responde en vivo, (3) si da el mismo número ante la misma entrada (reproducibilidad), porque la tarifa se cobra, (4) si puedo explicar por qué dio ese número, (5) cómo se comporta en casos raros (tarifa fija, rutas poco vistas) y (6) el esfuerzo de mantenerlo (reentrenar, versionar, depender de un proveedor).

## Ejercicio 1: una red neuronal frente al ensamblaje

Notebook: [`starter/ejercicio1_red_neuronal.ipynb`](./starter/ejercicio1_red_neuronal.ipynb), sobre [`starter/viajes_features.csv`](./starter/viajes_features.csv). Ya entrena el gradient boosting de la sesión pasada con la misma preparación y la misma división, importadas de [`starter/preparacion_taxis.py`](./starter/preparacion_taxis.py). Los 3 `TODO` son la red neuronal, cuántos parámetros aprendió y qué columnas usa más el ensamblaje. Córrelo completo una vez antes de tocar nada (**Run All**).

**Respuesta 1 (TODO 1):** sin resolver, la red sale peor que el ensamblaje y aparece una advertencia `ConvergenceWarning`. ¿Qué crees que significa? ¿Qué esperas al dejarla entrenar hasta 1000 iteraciones?

Que el entrenamiento se detuvo en las 200 iteraciones por defecto sin haber convergido: el error todavía bajaba y la red quedó a medias (error de prueba 1.69, peor que el ensamblaje con 1.28). Con 1000 iteraciones esperaba que convergiera y mejorara; así fue: paró sola en la iteración 692 y el error de prueba bajó a 1.17, mejor que el ensamblaje.

**Respuesta 2 (TODO 2):** una capa oculta de 64 neuronas recibe las 25 columnas preparadas y entrega una tarifa. ¿Cuántos números tiene que aprender?

1729 números. Capa oculta: 25 × 64 pesos + 64 sesgos = 1664. Capa de salida: 64 × 1 pesos + 1 sesgo = 65. Total 1664 + 65 = 1729. El ensamblaje, en cambio, no tiene una cuenta tan simple: son árboles con umbrales.

**Respuesta 3 (TODO 3):** ¿qué columna esperas que el ensamblaje use más? Si la app le muestra al conductor por qué la tarifa estimada es 70 dólares, ¿cuál de los dos modelos te permite responder?

`distancia_km`, que concentra casi toda la importancia (0.98). Con el ensamblaje puedo decirle al conductor qué variables pesaron (la distancia, si fue tarifa fija, si era hora pico) y seguir el camino de los árboles; con la red, los 1729 números no se traducen a una razón legible, así que el ensamblaje es el que me permite explicar los 70 dólares.

**Lo que confirmó la salida, TODO por TODO:**

Gradient boosting: error de prueba 1.2754 (entrenamiento 1.0705) en 0.21 s. Red neuronal: error de prueba 1.1695 (entrenamiento 1.0882) en 5.09 s, unas 25 veces más lenta pero con menos brecha entre entrenamiento y prueba (0.08 contra 0.20). Parámetros de la red: 1729. Las 3 columnas más importantes del ensamblaje: `distancia_km` (0.9824), `es_tarifa_fija` (0.0120) y `es_hora_pico` (0.0028).

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: tres soluciones sobre los mismos 20 viajes

Solo o en pareja. Notebook: [`starter/ejercicio2_tres_soluciones.ipynb`](./starter/ejercicio2_tres_soluciones.ipynb), sobre el mismo `viajes_features.csv`. Los pasos 1 a 3 tienen `TODO`; los pasos 4 y 5 solo tienen la comprobación.

1. Completa los `TODO` 1 a 3 y corre las celdas hasta la que escribe `prompt_llm.txt`: 30 viajes con su tarifa como ejemplos y 20 viajes sin tarifa.
2. Copia `prompt_llm.txt` completo en un LLM de chat. Guarda los 20 números que responda, uno por línea, en `respuestas_llm.txt`, en la carpeta `starter`.
3. Completa los pasos 4 y 5 y corre sus celdas y la de la comprobación hasta que todas digan `OK`. Los modelos ya están entrenados en el kernel: no hace falta volver a correr las celdas de arriba. Para el paso 5, busca el precio por millón de tokens de entrada del modelo que usaste en la página de precios de su proveedor.

**Respuesta 1:** ¿qué LLM usaste? Completa la tabla con los números de tu corrida.

Usé GPT-6.1 Terra (OpenAI) con esfuerzo de razonamiento medium. Precio de entrada: USD 1.00 por millón de tokens, el mismo para todos los esfuerzos de razonamiento (según agregadores de precios que citan a OpenAI; conviene confirmarlo en la [página oficial de precios](https://developers.openai.com/api/docs/pricing)). El prompt tiene 2902 caracteres, unos 726 tokens; 10 000 viajes son 500 prompts de 20 viajes, o sea unos 363 000 tokens.

| | Error en los 20 viajes | Costo de entrenar | Costo de 10 000 viajes al mes | ¿Puedes explicar una predicción? |
|---|---|---|---|---|
| Gradient boosting | 0.8957 | 0.21 s | Cómputo local, casi cero (sin costo por consulta) | Sí: importancias de columnas (`distancia_km` 0.98) y recorrido de los árboles |
| Red neuronal | 0.9637 | 5.09 s | Cómputo local, casi cero (sin costo por consulta) | No: 1729 parámetros sin una razón legible |
| LLM | 1.0360 | 0 s (no se entrena) | USD 0.36 (≈ 363 000 tokens de entrada a USD 1.00/M, sin contar la salida) | No: da un número sin mostrar de dónde sale |

**Respuesta 2:** corre el mismo prompt otra vez, en una conversación nueva. ¿Te dio los mismos 20 números? ¿Qué problema le trae eso a una app que le cobra al pasajero?

No. Los 20 números cambiaron: solo 3 coincidieron exactamente (los tres viajes de tarifa fija de 70). Las otras 16 respuestas cambiaron en promedio unos 0.4 dólares, y en el viaje JFK→JFK de 1.01 km el LLM pasó de 6.68 a 70.00 (real: 11.46), así que el error absoluto promedio pasó de 1.036 a 3.783. Sin ese viaje, los errores de las dos corridas son parecidos (0.84 y 0.90). Para una app que cobra, es un problema grave: la misma petición puede costar 6.68 o 70 según la corrida, no hay forma de reproducir ni auditar el cobro, y un solo error de este tipo (cobrar 70 por un viaje de 11) basta para perder la confianza del pasajero. Un modelo entrenado con semilla fija devuelve siempre el mismo número.

**Respuesta 3:** busca en tus 20 respuestas la peor predicción del LLM. ¿Qué tiene de particular ese viaje? ¿Lo habría aprendido el ensamblaje con las 2380 filas de entrenamiento?

El peor fue un viaje de JFK Airport a JFK Airport de solo 1.01 km: tarifa real 11.46, el LLM dijo 6.68 (error 4.78, el doble del siguiente peor). Lo particular es que es un viaje dentro del aeropuerto: el LLM estimó por la distancia corta, pero en esa ruta la tarifa nunca baja de cierto piso. El ensamblaje sí lo habría aprendido: en las 2380 filas de entrenamiento hay 7 viajes JFK→JFK con tarifas entre 12.39 y 18.67, y el ensamblaje predijo 12.74 (error 1.28). Aun así, son solo 7 ejemplos, así que es un patrón que el ensamblaje aprendió con pocos datos. El LLM solo vio 30 ejemplos, que probablemente no incluían ese caso.

**Si terminas antes:** el error en los 20 viajes de muestra no es el mismo que en los 595 de prueba. ¿Por qué no se mide el LLM sobre los 595, y qué tan confiable es una comparación sobre 20?

Porque el LLM no se puede correr de forma automática sobre 595 filas en el notebook: habría que pegar unos 30 prompts de 20 viajes a mano (o conectar una API), la respuesta cambia entre corridas y cada consulta cuesta. Sobre 20 viajes la comparación es poco confiable: el mismo gradient boosting tiene error 0.90 en esos 20 pero 1.275 en los 595, y al remuestrear 20 viajes de la prueba su error varía entre aproximadamente 0.85 y 1.88 (percentiles 5 y 95). Esa variación es mayor que las diferencias entre los tres modelos (0.90, 0.96 y 1.04), así que no puedo afirmar con 20 viajes cuál es mejor; solo que el LLM no parece estar muy lejos, y que el ranking de los 595 (la red mejor que el ensamblaje) ni siquiera coincide con el de los 20.

## Ejercicio 3: ¿qué solución conviene para tu proyecto?

Usa tu pipeline y la tabla de resultados de la sesión pasada. Esta vez no hay plantilla.

### Entregable 1: `comparar_proyecto.ipynb`

Un notebook, al lado de tu `pipeline_proyecto.py`, que importe de ahí tu preparación y tu división, y entrene el mejor ensamblaje de la sesión pasada y una red neuronal simple (`MLPRegressor` o `MLPClassifier`), y registre para cada uno la métrica de prueba, los segundos de entrenamiento y, para la red, la cantidad de parámetros.

### Entregable 2: la prueba del LLM

Elige 10 filas de tu conjunto de prueba y escribe un prompt con algunas filas de entrenamiento como ejemplos, como el de `prompt_llm.txt`. Pásalo a un LLM y registra su métrica sobre esas 10 filas, junto con la de tus dos modelos sobre las mismas 10. Si tu problema no se puede plantear así (por ejemplo, porque cada predicción necesita una historia larga), explica por qué; eso también es una respuesta.

### Entregable 3: la decisión

Una tabla con las tres opciones (métrica, costo, explicabilidad) y un párrafo que diga cuál usarías en tu proyecto y por qué, con los números de tu tabla.

Proyecto M5 (CA_1): predecir las unidades vendidas de un item al día siguiente. Notebook y pipeline en `psets/proyecto/modelado/` (`comparar_proyecto.ipynb`, `pipeline_proyecto.py`). División por fecha: últimas 8 semanas como prueba (170 744 filas); entrenamiento con una muestra de 200 000 filas. Métrica: error absoluto medio (MAE) en unidades.

| | MAE en prueba (170 744 filas) | MAE en 10 filas | Costo de entrenar | Costo al mes (≈ 90 000 predicciones) | Explicabilidad |
|---|---|---|---|---|---|
| Referencia: media de 28 días previos (sin modelo) | 1.108 | 1.396 | ninguno | ninguno | Total: es una regla |
| Gradient boosting | 1.090 | 1.405 | 16 s | cómputo local, casi cero | Sí: importancias y árboles |
| Red neuronal (2177 parámetros) | 1.071 | 1.018 | 16 s | cómputo local, casi cero | No |
| LLM (GPT-6.1 Terra, medium) | no se midió | 1.600 | no se entrena | ≈ USD 5.40 (600 tokens por prompt de 10 casos, USD 1.00/M de entrada) | No, y no es reproducible |

El LLM solo se probó en 10 filas porque no se puede pegar a mano sobre 170 744; con 10 filas la comparación es muy ruidosa (el LLM falló sobre todo en un caso donde se vendieron 16 unidades y dijo 7).

Usaría el **gradient boosting**. Los tres enfoques quedan muy cerca: 1.090 (ensamblaje) y 1.071 (red) de MAE en la prueba completa, contra 1.108 de la media de los 28 días previos, que no necesita modelo. La red es la mejor por 0.019 unidades (menos de 2%), una diferencia que no justifica perder la capacidad de explicar por qué se pronostica cierta cantidad, algo que sí ofrece el ensamblaje (importancias, árboles) y que importa para decidir cuánto reponer en tienda. Cuesta lo mismo de entrenar (16 s) y se ejecuta localmente sin costo por consulta. El LLM queda descartado: en las 10 filas tuvo el peor MAE (1.60 frente a 1.02 de la red y 1.41 del ensamblaje), cuesta unos USD 5.40 al mes por una sola tienda (y crecería con las demás), y su respuesta no es reproducible, como vi en el Ejercicio 2. Una advertencia: el modelo apenas supera a la regla de la media de 28 días, porque casi toda la señal ya está en `units_media_28`; antes de ponerlo en producción habría que ver si ese margen de 1.6% justifica mantener un modelo, o si conviene agregar features nuevas (por ejemplo precio relativo o promociones).

## Antes de la próxima sesión

**Lectura:** ["Version Controlling in Practice: Data, ML Model, and Code"](https://towardsdatascience.com/version-controlling-in-practice-data-ml-model-and-code-e13c518067dc/), Towards Data Science.

Dos compañeros reportan errores distintos para "el mismo" gradient boosting sobre los mismos datos de taxis. ¿Qué tendrías que saber de cada corrida para descubrir por qué no coinciden?

Tendría que saber, de cada corrida: la versión del código (commit), la versión y el hash de los datos, la división de entrenamiento y prueba (semilla), los hiperparámetros, la semilla aleatoria del modelo, las versiones de las librerías (scikit-learn, Python), la métrica y cómo se calculó, y el entorno. Con MLflow se registra todo eso por corrida, así que bastaría comparar las dos.
