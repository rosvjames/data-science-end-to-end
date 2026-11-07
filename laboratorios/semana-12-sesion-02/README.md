# Semana 12, Sesión 2: Despliegue de modelos como servicio de predicción

> Objetivo de la sesión: exponer el modelo entrenado de tu proyecto como un servicio de predicción mediante una API, empaquetado en un contenedor, con pruebas de su contrato de entrada y salida.

**Lectura previa de esta sesión:** ["Journey to Full-Stack Data Scientist: Model Deployment"](https://towardsdatascience.com/journey-to-full-stack-data-scientist-model-deployment-f385f244ec67/), Towards Data Science.

**Referencia de esta sesión:** [Machine Learning Zoomcamp, Módulo 5 (DataTalksClub)](https://github.com/DataTalksClub/machine-learning-zoomcamp).

## Requisitos antes de esta sesión

Nada nuevo que instalar: FastAPI y uvicorn ya llegaron con el contenedor reconstruido la sesión pasada. Los laboratorios de hoy son scripts y un `Dockerfile`. El servicio escucha en el puerto 8000: cuando lo levantes, aparece en la pestaña **Ports** como "Servicio de predicción (Semana 12)", y su documentación interactiva queda en la ruta `/docs` de ese puerto.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué pasos separan un modelo entrenado en un notebook de un modelo que otra aplicación puede usar?**

_(tu respuesta)_

**¿Para qué usa el artículo un contenedor, si el servicio ya corre en la máquina de quien lo escribió?**

_(tu respuesta)_

## Pregunta de apertura

La sesión pasada, la app leía las tarifas de una tabla calculada de noche. Cuando un pasajero escribe un destino que no estaba reservado, no hay ninguna fila que leer. ¿Qué tendría que existir para que la app le pregunte al modelo en ese momento, y qué le mandaría?

Tendría que existir un servicio en línea (una API) con el modelo ya cargado, siempre disponible, al que la app le envíe una petición por viaje. Le mandaría lo que la app conoce en ese momento: fecha y hora, zona de origen y destino, distancia, pasajeros y método de pago. El servicio calcularía las demás features igual que en el entrenamiento y respondería con la tarifa estimada. _(Razonamiento propio; no pude leer el artículo.)_

## Ejercicio 1: la tarifa, como servicio

Carpeta: [`starter/ejercicio1/`](./starter/ejercicio1/). [`servicio.py`](./starter/ejercicio1/servicio.py) es una API de FastAPI con dos rutas: `/salud`, que dice si el servicio está vivo y tiene su modelo, y `/predecir`, que recibe un viaje como JSON y devuelve la tarifa estimada. El viaje llega como lo conoce la app (fecha y hora, zonas, distancia, pasajeros, método de pago), y [`features_taxis.py`](./starter/ejercicio1/features_taxis.py) calcula el resto de las features igual que se calcularon para entrenar. [`test_servicio.py`](./starter/ejercicio1/test_servicio.py) prueba la API sin levantarla, y el [`Dockerfile`](./starter/ejercicio1/Dockerfile) la empaqueta. Los 5 `TODO`: el esquema de entrada, la predicción, dos pruebas y el comando del contenedor.

Desde la carpeta del ejercicio, corre todo una vez antes de tocar nada:

```
python entrenar.py
pytest -v
uvicorn servicio:app --port 8000
```

Con el servicio levantado, abre el puerto 8000 desde la pestaña **Ports**, agrega `/docs` a la dirección y prueba `/predecir` con **Try it out**. También desde otra terminal:

```
curl -X POST localhost:8000/predecir -H "Content-Type: application/json" -d '{"fecha_hora_inicio": "2026-11-05 08:30", "zona_origen": "Midtown", "zona_destino": "JFK Airport", "distancia_km": 26.4, "pasajeros": 2, "metodo_pago": "tarjeta"}'
```

**Respuesta 1 (antes de los TODO):** sin resolver, `/salud` dice que el modelo está cargado, `/predecir` responde 200 y `pytest` dice `3 passed`. ¿Qué de esa salida debería preocuparte?

Que todo "funciona" sin haber implementado nada: `/predecir` responde 200 con una tarifa que no viene del modelo (siempre 0.0) y las 3 pruebas pasan porque, como en la sesión pasada, las pruebas sin `assert` no comprueban nada. El código 200 y las pruebas en verde no prueban que la respuesta sea correcta; hay que revisar el contenido de la respuesta.

**Respuesta 2 (TODO 1):** con el esquema completo, ¿qué esperas que responda el servicio a un viaje sin `distancia_km`? ¿Y a uno sin `zona_origen`?

A un viaje sin `distancia_km` esperaba una respuesta normal (200): es opcional (valor por defecto `None`) y la preparación del pipeline la imputa con la mediana; en la práctica respondió 200 con 68.56 frente a 70.39 con distancia. A un viaje sin `zona_origen`, un error 422 (campo obligatorio faltante), sin llegar al modelo.

**Respuesta 3 (TODO 2):** el modelo se entrenó con `hora_sin`, `hora_cos` y `es_hora_pico`, pero la app manda solo la fecha y hora. ¿Qué pasaría si el servicio calculara `es_hora_pico` con otras horas que las del entrenamiento?

El modelo recibiría valores de `es_hora_pico` con otro significado que los que aprendió: se equivocaría sin dar ningún error ni advertencia, porque la columna seguiría siendo un 0 o un 1 válido. Por eso el servicio importa `agregar_features` de `features_taxis.py`, el mismo código con el que se construyeron las features de entrenamiento, y no vuelve a escribirlas.

**Respuesta 4 (TODO 3 y 4):** el código 422 del viaje sin zona de origen, ¿lo produce tu código o FastAPI? ¿La petición llega al modelo?

Lo produce FastAPI (con pydantic), antes de ejecutar mi función: al faltar `zona_origen`, un campo obligatorio de `Viaje`, rechaza la petición con 422 y un mensaje que dice qué campo falta. La petición no llega al modelo ni a `predecir`.

**Respuesta 5 (TODO 5):** construye y corre la imagen con el `CMD` sin resolver (`docker build -t servicio-tarifa .` y `docker run -p 8000:8000 servicio-tarifa`). El log dice que uvicorn está corriendo, pero `curl localhost:8000/salud` falla. ¿Por qué?

Porque uvicorn, sin `--host`, escucha en 127.0.0.1, es decir, solo dentro del contenedor. El log dice que está corriendo, pero el puerto publicado (`-p 8000:8000`) reenvía el tráfico a la interfaz externa del contenedor, donde no hay nadie escuchando, así que la conexión desde fuera falla. Con `--host 0.0.0.0` escucha en todas las interfaces. (Esta respuesta es de conocimiento general; sí construí y corrí la imagen con el `CMD` corregido: `/salud` y `/predecir` respondieron desde fuera del contenedor.)

**Lo que respondió el servicio:**

Viaje de Midtown a JFK Airport (26.4 km, 2 pasajeros, tarjeta, 2026-11-05 08:30): `{"tarifa_estimada": 70.39}`. Viaje sin zona de origen: código 422 con `{"detail": [{"type": "missing", "loc": ["body", "zona_origen"], "msg": "Field required", ...}]}`.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: el fraude, en el momento del pago

Solo o en pareja. Carpeta: [`starter/ejercicio2/`](./starter/ejercicio2/). La sesión pasada, los pagos se revisaban al día siguiente. Ahora la empresa quiere decidir en el momento del cobro si un pago va a revisión. [`servicio_fraude.py`](./starter/ejercicio2/servicio_fraude.py) expone el mismo gradient boosting en `/evaluar_pago`, que devuelve la probabilidad de fraude y la decisión. Mismo esqueleto del Ejercicio 1: los pasos 1 a 3 tienen `TODO` (el esquema, la probabilidad y la prueba del pago válido); el paso 4 (la decisión con el umbral) y el paso 5 (la prueba del pago sin monto) solo tienen un comentario. El `Dockerfile` ya está completo. Primero `python entrenar_fraude.py`; después resuelve y corre `python comprobar.py` hasta que los cinco pasos digan `OK`.

**Respuesta 1:** levanta el servicio y evalúa dos pagos: uno de madrugada, por app, con tarjeta nueva, dos intentos fallidos y ningún viaje previo; otro de la tarde, con tarjeta conocida y 22 viajes previos. ¿Qué probabilidad y qué decisión recibió cada uno?

El pago de madrugada (por app, tarjeta nueva, dos intentos fallidos, sin viajes previos): probabilidad 0.9996, decisión `revisar: true`. El pago de la tarde (tarjeta conocida, 22 viajes previos): probabilidad 0.0159, `revisar: false`. (Probado con la API en la misma máquina.)

**Respuesta 2:** el servicio devuelve la decisión (`revisar`) además de la probabilidad. ¿Qué gana la app con eso? ¿Qué tendría que cambiar si la empresa decide mañana que el umbral es 0.20?

La app no tiene que saber el umbral ni compararlo: la regla de negocio vive en un solo lugar y la app solo actúa sobre `revisar`. Si el umbral pasa a 0.20, se cambia `UMBRAL` en el servicio y se vuelve a construir y desplegar la imagen; las aplicaciones que lo usan no cambian, mientras que si cada una comparara la probabilidad con su propio umbral, habría que actualizar todas.

**Respuesta 3:** el mismo pago, evaluado por este servicio y por el lote de la sesión pasada, ¿da la misma probabilidad? ¿Qué tiene que ser igual en los dos para que así sea?

Sí, debe dar la misma. Lo comprobé con tres pagos de `pagos_taxi.csv`: 0.0782, 0.0598 y 0.9053 por las dos vías. Tiene que ser igual: el archivo del modelo (la misma versión entrenada), las features (`agregar_features` y `preparacion` de `preparacion_pagos.py`, con las mismas columnas en el mismo orden) y las versiones de las librerías con las que se guardó y se carga el modelo.

**Si terminas antes:** manda a `/evaluar_pago` un pago con `"monto": "cuarenta"`. ¿Qué responde el servicio, y qué línea de `servicio_fraude.py` produce esa respuesta?

Responde 422 con `{"detail": [{"type": "float_parsing", "loc": ["body", "monto"], "msg": "Input should be a valid number, unable to parse string as a number", "input": "cuarenta"}]}`. Lo produce la línea `monto: float` de la clase `Pago` en `servicio_fraude.py`: pydantic valida los tipos antes de que corra `evaluar_pago`.

## Ejercicio 3: el servicio de tu proyecto

Usa tu proyecto en [`psets/proyecto/`](../../psets/README.md) y el modelo final que registraste en MLflow (Semana 11). Esta vez no hay plantilla. Aunque tu proyecto se despliegue por lotes, el servicio también se construye: es la forma en que otro sistema (tu propio lote, un tablero, otra aplicación) le pide una predicción a tu modelo.

### Entregable 1: el servicio, en `psets/proyecto/servicio/`

- Un script que exporte tu modelo final desde MLflow a `servicio/modelo.joblib` (`mlflow.sklearn.load_model("runs:/<run_id>/modelo")` y `joblib.dump`). El archivo no se sube: se regenera con ese script.
- `servicio/api.py`, con `/salud` y una ruta de predicción. El esquema de entrada recibe los datos como los conoce quien llama, y el servicio calcula las features con las mismas funciones de tu `modelado/pipeline_proyecto.py`, importadas desde ahí (`from modelado.pipeline_proyecto import ...`), no copiadas.
- `servicio/Dockerfile` y `servicio/requirements.txt`, con la misma versión de scikit-learn con que entrenaste. La imagen se construye desde `psets/proyecto/`, porque necesita `modelado/` además de `servicio/`: `docker build -f servicio/Dockerfile -t <tu-servicio> .`

El servicio corre desde `psets/proyecto/`: `uvicorn servicio.api:app --port 8000`. El archivo [`psets/proyecto/conftest.py`](../../psets/proyecto/conftest.py) hace que las pruebas también encuentren `modelado/` desde ahí.

### Entregable 2: `servicio/test_api.py`

Al menos tres pruebas con `TestClient`: `/salud`, una predicción válida con un modelo de prueba (no tu `modelo.joblib`, que no existe en GitHub Actions) y una entrada inválida que recibe 422. El workflow de la sesión pasada ya corre todo lo que hay en `psets/proyecto`: en tu próximo push, GitHub corre también estas pruebas.

### Entregable 3: respuestas

En `proyecto/README.md`, agrega la sección **Cómo correr el servicio**: cómo se exporta el modelo, cómo se construye y se levanta el contenedor, y un ejemplo de petición con su respuesta.

**¿Qué datos recibe tu servicio, y cuáles de tus features calcula él mismo? ¿Cómo sabes que las calcula igual que en el entrenamiento?**

Recibe el departamento del producto, la fecha a predecir, el precio vigente, si es día SNAP o de evento, y las ventas diarias recientes del producto (mínimo 28 días, hasta el día anterior). Calcula él mismo `units_lag_7` y `units_media_28` (con `agregar_features`, importada de `modelado/pipeline_proyecto.py`) y el calendario (`wday`, `month`, `is_weekend`, con `features_de_calendario`, de la misma ruta). Sé que las calcula igual que en el entrenamiento porque no hay una segunda copia del cálculo: el servicio llama a las mismas funciones que el pipeline de entrenamiento, y lo verifiqué de tres formas: pruebas con series escritas a mano (hace 7 días = 34 y media de 28 días = 26.5 para ventas 1 a 40), una prueba que compara el calendario con el de M5 (sábado = 1) y una comparación de `features_de_calendario` contra las columnas reales de la OBT en 1941 fechas, sin diferencias.

**Pega una petición a tu servicio corriendo en el contenedor, y su respuesta:**

Contenedor construido con `docker build -f servicio/Dockerfile -t servicio-demanda .` desde `psets/proyecto/`, y levantado con `docker run -p 8000:8000 servicio-demanda` (yo lo corrí publicando en otro puerto local):

```bash
curl -X POST localhost:8000/predecir -H "Content-Type: application/json" -d '{"fecha": "2016-05-22", "dept_id": "FOODS_1", "sell_price": 2.24, "is_snap": false, "is_event_day": false, "ventas_recientes": [1, 1, 0, 2, 0, 0, 0, 0, 1, 1, 0, 6, 1, 0, 3, 0, 0, 0, 2, 0, 0, 2, 3, 1, 0, 0, 0, 1, 0, 0]}'
```

Respuesta: `{"unidades_estimadas":0.99,"version_modelo":"2775572759c4"}` (las ventas reales ese día fueron 0). `GET /salud` respondió `{"estado":"ok","modelo_cargado":true,"version_modelo":"2775572759c4"}`, y un historial de 3 días recibió 422 (`List should have at least 28 items`).

## Antes de la próxima sesión

**Lectura:** ["What Is Model Governance?"](https://www.ibm.com/think/topics/model-governance), IBM.

Tu servicio carga `modelo.joblib`, el archivo que exportaste hoy. Si la semana que viene reentrenas y vuelves a exportar, el archivo se reemplaza. Si mañana un usuario reclama por una predicción de hoy, ¿cómo sabrías qué modelo la produjo? ¿Y cómo volverías al modelo anterior si el nuevo resulta peor?

Habría que registrar con cada predicción la versión del modelo que la produjo (como la huella MD5 del archivo o el `run_id` de MLflow del que se exportó) y guardarla junto con la petición; sin eso, `modelo.joblib` reemplazado no dice nada. Para volver al modelo anterior habría que conservar los archivos de cada versión (o poder volver a exportarlos desde MLflow con su `run_id`) y redesplegar la imagen con esa versión; es más fácil si el servicio carga un modelo con versión explícita en vez de un archivo que se sobrescribe. _(Razonamiento propio; no leí el artículo.)_
