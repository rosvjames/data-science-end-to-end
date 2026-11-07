# Semana 11, Sesión 1: Gestión y trazabilidad de experimentos: eligiendo el modelo ganador con evidencia

> Objetivo de la sesión: registrar de forma trazable los parámetros, métricas y artefactos de las corridas de entrenamiento de las dos sesiones anteriores, y elegir el modelo final de tu proyecto con esa evidencia.

**Lectura previa de esta sesión:** ["Version Controlling in Practice: Data, ML Model, and Code"](https://towardsdatascience.com/version-controlling-in-practice-data-ml-model-and-code-e13c518067dc/), Towards Data Science.

**Referencia de esta sesión:** [ML Experiment Tracking (documentación oficial de MLflow)](https://mlflow.org/docs/latest/ml/tracking/).

## Requisitos antes de esta sesión

Hoy se agrega una herramienta: MLflow, que registra cada corrida de entrenamiento. Como en un equipo de datos, el registro vive en un servidor de seguimiento (tracking server), no en tu notebook: el Codespace levanta uno en el puerto 5050 cada vez que inicia, y los notebooks lo encuentran por la variable de entorno `MLFLOW_TRACKING_URI`.

Si tu Codespace se creó antes de esta sesión, sincroniza tu fork y reconstruye el contenedor (`Ctrl+Shift+P` o `Cmd+Shift+P` → "Codespaces: Rebuild Container"; en tu laptop, "Dev Containers: Rebuild Container"). Reconstruir instala MLflow y configura el servidor; tus archivos no se pierden. Al terminar, comprueba desde una terminal:

```
bash .devcontainer/verificar.sh
```

Las últimas líneas deben decir `mlflow, version 2.17.2` y `servidor de MLflow: responde en http://127.0.0.1:5050`. Si el servidor no responde (por ejemplo, después de detener y volver a abrir el Codespace sin que arranque), levántalo a mano con `bash .devcontainer/mlflow-server.sh`.

La interfaz de MLflow se abre desde la pestaña **Ports** de VS Code: el puerto 5050, "MLflow (Semana 11)", con el ícono del globo. Ahí ves cada experimento, sus corridas, y puedes compararlas lado a lado.

Los laboratorios de hoy son notebooks, como los de la Semana 10, y la preparación se importa de `preparacion_taxis.py`. El registro (la base de datos del servidor y los modelos guardados) queda en la carpeta `.mlflow/` de la raíz del repositorio, que no se sube (está en `.gitignore`): lo que entregas es el notebook y la tabla de corridas que exporta.

**Si trabajas en tu laptop sin el contenedor (Opción B del README):** instala con `pip install -r requirements.txt` y, en una terminal aparte desde la raíz de tu fork, levanta el mismo servidor con `mlflow server --backend-store-uri sqlite:///.mlflow/mlflow.db --artifacts-destination .mlflow/artefactos --port 5050`. Antes de abrir los notebooks, define la variable `MLFLOW_TRACKING_URI=http://127.0.0.1:5050`. Sin esa variable, MLflow guarda el registro en una carpeta `mlruns` al lado de cada notebook, sin servidor: los notebooks también funcionan, pero cada carpeta tiene su propio registro.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué tres cosas hay que versionar en un proyecto de machine learning, y con qué herramienta versiona el autor cada una?**

_(tu respuesta)_

**¿Por qué no alcanza con Git para versionar los datos?**

Porque Git guarda archivos de texto pequeños y compara líneas: un CSV o un conjunto de datos grande, o un modelo binario, hace el repositorio pesado y lento, y un cambio de una fila no se puede revisar como un cambio de código. Los datos suelen cambiar o crecer fuera del repositorio, y además hace falta saber qué versión exacta de los datos produjo cada modelo; por eso se usa una herramienta aparte (o al menos una huella del archivo, como en este laboratorio) que se registra junto con la corrida. _(Respuesta general: no pude abrir el artículo, que devolvió un error 403; compárala con lo que dice.)_

## Pregunta de apertura

Dos compañeros reportan errores distintos para "el mismo" gradient boosting sobre los mismos datos de taxis. ¿Qué tendrías que saber de cada corrida para descubrir por qué no coinciden?

Tendría que saber, de cada corrida: la versión del código (commit), la versión y la huella de los datos, cómo se dividieron los datos (semilla o fecha de corte), los hiperparámetros, la semilla del modelo, las versiones de las librerías, la métrica y cómo se calculó. Con MLflow todo eso queda registrado por corrida y se pueden comparar lado a lado.

## Ejercicio 1: registrar cada corrida con MLflow

Notebook: [`starter/ejercicio1_registrar_corridas.ipynb`](./starter/ejercicio1_registrar_corridas.ipynb), sobre [`starter/viajes_features.csv`](./starter/viajes_features.csv), con la preparación de [`starter/preparacion_taxis.py`](./starter/preparacion_taxis.py). Entrena el bosque y el gradient boosting de la Semana 10, y después la corrida de un compañero. Los 4 `TODO` son el registro. Córrelo completo una vez antes de tocar nada (**Run All**).

**Respuesta 1 (antes de los TODO):** sin resolver, el notebook entrena los tres modelos e imprime sus errores. ¿Cuál de los dos gradient boosting tiene razón? ¿Qué parte de la salida te permite saberlo, y qué parte no?

Ninguno "tiene razón": los dos están bien calculados, pero sobre divisiones distintas de los datos. La salida lo deja ver en el número que imprime (`division 42` y `division 7`): 1.2754 con la semilla 42 y 1.1867 con la semilla 7. Lo que la salida no dice es todo lo demás: los hiperparámetros, qué archivo de datos se usó, cuántas filas, ni se puede volver a consultar después de reiniciar el kernel.

**Respuesta 2 (TODO 2 y 3):** de todo lo que se puede registrar de una corrida, ¿qué crees que explica la diferencia entre los dos gradient boosting? ¿Qué parámetro esperas ver distinto en la tabla del paso 5?

La semilla de la división de los datos (42 contra 7): el modelo, sus hiperparámetros y el CSV son los mismos. En la tabla del paso 5 esperaba ver `params.semilla_division` distinta (7 contra 42) y los demás parámetros iguales, incluida la huella de los datos.

**Respuesta 3 (TODO 4):** el registro ya tiene los parámetros y las métricas. ¿Para qué guardar además el modelo entrenado?

Porque los parámetros y las métricas solo describen la corrida; el modelo entrenado es lo que se puede volver a cargar para reproducir el número exacto, comparar sus predicciones o ponerlo en producción (Semana 12), sin tener que reentrenar ni confiar en que el código, los datos y las librerías de hoy den lo mismo.

**Lo que mostró la tabla del paso 5:**

| Corrida | Error en prueba | Semilla de la división | Huella de los datos |
|---|---|---|---|
| gradient boosting (compañero) | 1.1867 | 7 | 4800204d50c0 |
| gradient boosting (mío) | 1.2754 | 42 | 4800204d50c0 |
| bosque aleatorio (200 árboles) | 1.2989 | 42 | 4800204d50c0 |

La huella es la misma en las tres corridas, así que usaron el mismo archivo; la diferencia entre los dos gradient boosting viene solo de la semilla de la división.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: comparar con evidencia y elegir

Solo o en pareja. Notebook: [`starter/ejercicio2_comparar_y_elegir.ipynb`](./starter/ejercicio2_comparar_y_elegir.ipynb), sobre el mismo `viajes_features.csv`. Mismo esqueleto del Ejercicio 1, con los cinco modelos de la Semana 10 en un experimento propio. Los pasos 1 a 3 tienen `TODO`; los pasos 4 y 5 solo tienen la comprobación. Complétalos hasta que todas digan `OK`.

**Respuesta 1:** ¿qué modelo quedó primero en el registro, y por cuánto le gana al segundo?

La red neuronal, con 1.1695 de error en prueba, frente a 1.2754 del gradient boosting (segundo): le gana por 0.106, un 8.3%. Luego quedan el bosque (1.2989), ridge (2.5565) y la línea base (12.5308).

**Respuesta 2:** el paso 5 carga el modelo ganador desde el registro y vuelve a calcular su error. ¿Qué te garantiza que coincida con el número registrado? ¿Qué no te garantiza sobre ese modelo?

Garantiza que el pipeline guardado (preparación y modelo) vuelve a dar exactamente la misma predicción sobre los mismos datos de prueba: el error recalculado (1.169505) coincide con el registrado a más de 9 decimales. No garantiza que ese modelo sea bueno con datos nuevos ni con otra división (el mismo gradient boosting dio 1.1867 con otra semilla), ni que cargue igual con otras versiones de scikit-learn, ni nada sobre su comportamiento en producción.

**Respuesta 3:** si mañana alguien cambia una fila de `viajes_features.csv` y vuelve a entrenar, ¿cómo lo notarías mirando solo el registro?

Por el parámetro `huella_datos` de la corrida: el código y los hiperparámetros serían los mismos, pero la huella del CSV sería distinta a la de las corridas anteriores (4800204d50c0), y el error podría cambiar. Cambiar un solo byte del archivo cambia la huella.

**Si terminas antes:** abre la interfaz de MLflow (pestaña **Ports**, puerto 5050), entra al experimento `tarifa-taxis-comparacion`, selecciona las cinco corridas y compáralas lado a lado con **Compare**. Además del error, ¿qué te dice el registro de la red neuronal que no te diría una tabla escrita a mano?

Con lo que quedó registrado: los hiperparámetros completos de la red (`hidden_layer_sizes`, `max_iter`, `solver`, `activation`, etc., incluidos los que no escribí yo), cuánto tardó entrenar (60 s, frente a 0.19 s del gradient boosting y 1.1 s del bosque), el modelo guardado para volver a cargarlo, y la huella de los datos y la semilla de la división con las que se hizo. Una tabla a mano no tiene nada de eso salvo lo que alguien se acuerde de anotar. No abrí la interfaz de MLflow; esta respuesta sale de los datos registrados.

## Ejercicio 3: el registro de tu proyecto

Usa tu `pipeline_proyecto.py` y los modelos que entrenaste en las dos sesiones de la Semana 10. Esta vez no hay plantilla.

### Entregable 1: `experimentos_proyecto.ipynb`

Un notebook, al lado de tu `pipeline_proyecto.py`, que importe de ahí la preparación y la división y registre en MLflow, en un experimento con el nombre de tu proyecto, una corrida por cada modelo de la Semana 10 (línea base, modelo lineal, ensamblaje, red neuronal). Cada corrida registra:

- Los hiperparámetros del modelo.
- Cómo se dividieron los datos (la semilla, o la fecha de corte si divides por fecha) y la huella del archivo de datos.
- La métrica de tu proyecto en entrenamiento y en prueba, y los segundos de entrenamiento.
- El pipeline entrenado, como artefacto.

Al final, el notebook marca la corrida que eliges como final (`candidato` = `final`), carga su modelo desde el registro y comprueba que reproduce la métrica registrada.

### Entregable 2: `corridas_proyecto.csv`

La tabla de corridas de tu experimento, exportada con `mlflow.search_runs(...).to_csv("corridas_proyecto.csv", index=False)` desde el mismo notebook. Antes de hacer commit, borra las corridas de prueba del experimento de tu proyecto (en la interfaz de MLflow: selecciónalas y **Delete**), reinicia el kernel y corre todo: la tabla tiene que salir de una corrida completa.

### Entregable 3: la decisión

**¿Qué modelo elegiste como final? Escribe su `run_id` y los números del registro que sostienen la decisión.**

Elegí el **gradient boosting**, `run_id` `7ca7b0e729c148d186cf4bd02fbce8ec` (etiqueta `candidato` = `final`). Experimento `m5-demanda-CA_1`, MAE en prueba (últimas 8 semanas, 170 744 filas): red neuronal 1.0713 (112 s de entrenamiento), **gradient boosting 1.0895** (16.6 s), línea base (media de 28 días) 1.1082, ridge 1.1190. La red tiene el menor error, pero solo por 0.018 unidades (1.7%), tarda unas 7 veces más y no se puede explicar; el gradient boosting se acerca bastante y sí. Cargado desde el registro, el modelo reproduce exactamente el error registrado (1.0895). Tabla completa en `psets/proyecto/modelado/corridas_proyecto.csv`.

**Si otra persona clona tu repositorio, ¿qué necesita para obtener exactamente el mismo número? ¿Qué de eso quedó registrado en MLflow y qué no?**

Necesita: el mismo archivo de datos (`obt_sales_CA_1.csv.gz`, que no está en el repo: se exporta de Snowflake; su huella es `2aebb531e268`), el mismo código (`pipeline_proyecto.py` y `experimentos_proyecto.ipynb`, en el mismo commit), las mismas versiones de librerías (`requirements.txt`: Python 3.11, scikit-learn 1.5.2, etc.), y las semillas y la división (`random_state=42`, muestra de 200 000 filas de entrenamiento, últimos 56 días como prueba). **Quedó registrado en MLflow:** los hiperparámetros, la huella de los datos, los días de prueba, el tamaño de la muestra y las filas, las métricas, los segundos y el pipeline entrenado (con su lista de dependencias). **No quedó registrado:** de dónde sale el archivo y cómo se exportó, el commit de git del código, la semilla del muestreo de las 200 000 filas (está en el código, no en el registro) y el registro mismo: `.mlflow/` está en `.gitignore`, así que quien clona el repositorio no recibe las corridas, solo la tabla `corridas_proyecto.csv`.

## Antes de la próxima sesión

**Lectura:** ["How Metrics (and LLMs) Can Trick You: A Field Guide to Paradoxes"](https://towardsdatascience.com/how-metrics-and-llms-can-trick-you-a-field-guide-to-paradoxes/), Towards Data Science.

Hoy elegiste el modelo con menor error sobre los 595 viajes de prueba. ¿Cuánto cambiaría ese error si la división hubiera sido otra? ¿Lo viste en algún lado del registro?

Cambiaría bastante: con la semilla 42 el gradient boosting da 1.2754 y con la semilla 7 da 1.1867, una diferencia de 0.09 (7%) solo por la división, parecida a la distancia entre la red (1.1695) y el gradient boosting (1.2754). Sí lo vi: en la tabla del paso 5, en las dos corridas del gradient boosting con distinta `semilla_division`. Con 595 viajes de prueba, un solo número es poca evidencia.
