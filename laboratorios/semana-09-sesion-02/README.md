# Semana 9, Sesión 2: Pipeline reproducible de features

> Objetivo de la sesión: construir un pipeline de transformación reproducible con scikit-learn (imputación, codificación, escalado) para el dataset de tu proyecto, que evite la fuga de información entre entrenamiento y validación.

**Lectura previa de esta sesión:** ["The Dreaded Antagonist: Data Leakage in Machine Learning"](https://towardsdatascience.com/the-dreaded-antagonist-data-leakage-in-machine-learning-5f08679852cc/), Towards Data Science.

**Referencia de esta sesión:** [Pipelines and composite estimators (documentación oficial de scikit-learn)](https://scikit-learn.org/stable/modules/compose.html).

## Requisitos antes de esta sesión

scikit-learn ya viene en el Codespace. En tu laptop, instálalo con `pip install -r requirements.txt` desde la raíz del repositorio. Verifica con:

```
python3 -c "import sklearn; print(sklearn.__version__)"
```

Este laboratorio usa `sparse_output=False` en `OneHotEncoder`, disponible desde scikit-learn 1.2. El `requirements.txt` del repositorio ya fija una versión posterior.

Ten a mano tu notebook de features de la sesión pasada. Los tres ejercicios de hoy son scripts, no notebooks: un pipeline de preparación es código de producción, que tiene que correr igual cada vez y que otros archivos importan. En el Ejercicio 3, la preparación de tu proyecto pasa del notebook donde la probaste a ese script.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué es la fuga de información, y por qué un modelo con fuga puede verse excelente en la evaluación y fallar en producción?**

Es cuando información que el modelo no tendría al predecir (del futuro o del conjunto de prueba) se cuela en el entrenamiento. El modelo se ve excelente en la evaluación porque "hace trampa" con esa información, y falla en producción, donde no existe. _(general, sin leer el artículo)_

**El artículo describe varias formas en que se produce una fuga. ¿Cuál de ellas viste la sesión pasada con la duración del viaje?**

La fuga por usar una variable que solo se conoce después del evento: la duración del viaje (y la propina), que no existen al pedir el taxi pero sí están en el dataset. _(general, sin leer el artículo)_

## Pregunta de apertura

Para escalar la distancia, le restas la media y la divides por la desviación estándar. ¿Con qué viajes calculas esa media: con todos, o solo con los de entrenamiento? ¿Cambia algo?

Solo con los de entrenamiento. Sí cambia: si la media incluye viajes de prueba, el conjunto de prueba influye en el entrenamiento (fuga) y el error en prueba sale demasiado optimista.

## Ejercicio 1: encontrar y corregir la fuga

Archivo: [`starter/ejercicio1_fuga.py`](./starter/ejercicio1_fuga.py), sobre [`starter/viajes_features.csv`](./starter/viajes_features.csv): los viajes de taxi con las features de la sesión pasada, sin los errores confirmados, y con la distancia 0 y los 0 pasajeros marcados como faltantes. La primera parte del script es el código de un compañero: imputa y escala la distancia y los pasajeros con todo el dataset, después divide en entrenamiento y prueba, y entrena una regresión lineal. La segunda parte es la versión correcta, con 3 `TODO`. Córrelo una vez antes de tocar nada:

```
cd laboratorios/semana-09-sesion-02/starter
python3 ejercicio1_fuga.py
```

**Respuesta 1, antes de ver la solución:** en la versión del compañero, ¿en qué línea entra el conjunto de prueba al entrenamiento? ¿Qué número de la salida lo delata?

En la línea donde se ajusta y se aplica el imputador y el escalador sobre todo `X` (`escalador.fit_transform(imputador.fit_transform(X))`), antes de `train_test_split`: calculan la media con todas las filas. El número que lo delata es que el escalador vio 2975 filas, no las 2380 de entrenamiento.

**Respuesta 2 (TODO 1 y 3):** sin resolver, la versión correcta dice que tiene 2975 filas de prueba. ¿Qué está midiendo ese error, si prueba y entrenamiento son las mismas filas?

Nada útil: con `X_ent = X` y `X_prueba = X`, el modelo se mide con las mismas filas con que aprendió; ese error es el de entrenamiento, no el de prueba, y subestima el error real.

**Respuesta 3:** ¿cuánto esperas que cambie el error absoluto medio en prueba al corregir la fuga? Si casi no cambia, ¿significa que no había fuga?

Casi nada: salió 2.5375 con fuga y 2.5373 sin fuga. Que casi no cambie no significa que no había fuga: el escalador de una regresión lineal es una transformación lineal y la media cambia muy poco con 2975 contra 2380 filas; con otros modelos o con más fuga la diferencia sería grande. La fuga es un error de método, se corrige aunque el número no se mueva.

**Lo que confirmó la salida, TODO por TODO:**

El escalador del compañero vio 2975 filas (media de distancia 8.5034); el correcto, 2380 (media 8.5576). Errores absolutos medios en prueba: 2.5375 con fuga y 2.5373 sin ella.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: el pipeline completo

Solo o en pareja. Archivo: [`starter/ejercicio2_pipeline.py`](./starter/ejercicio2_pipeline.py), sobre el mismo `viajes_features.csv`. Completa los 5 `TODO`: división, `ColumnTransformer` con tres grupos de columnas, `fit` solo con entrenamiento, verificación de las medianas, y un viaje desde una zona que el entrenamiento nunca vio. Al final, el script imprime una comprobación por TODO: complétalos hasta que todas digan `OK`.

```
python3 ejercicio2_pipeline.py
```

**Respuesta 1:** ¿cuántas columnas quedan después de preparar los datos? Explica de dónde sale ese número a partir de los tres grupos de columnas.

Quedan 25 columnas: 2 numéricas + 5 ya listas + 18 de las categóricas (8 de `zona_origen`, 8 de `zona_destino` y 2 de `metodo_pago`, una por categoría).

**Respuesta 2:** ¿las medianas que aprendió el imputador coinciden con las de entrenamiento o con las de todo el dataset? ¿Qué demuestra eso?

Coinciden con las de entrenamiento: [6.94, 1.0], y no con las de todo el dataset ([6.93, 1.0], distinta en la distancia). Demuestra que el imputador aprendió solo con entrenamiento.

**Respuesta 3:** ¿qué le pasa al viaje desde el Bronx? ¿Qué habría pasado con `pd.get_dummies` aplicado por separado a ese viaje?

Queda con todas las columnas de `zona_origen` en 0: `handle_unknown="ignore"` codifica una categoría nueva como ceros, sin error. Con `pd.get_dummies` aplicado solo a ese viaje se habría creado una columna `zona_origen_Bronx` que el modelo no conoce, y no estarían las otras 8 columnas: la forma no coincidiría con la del entrenamiento.

## Ejercicio 3: el pipeline de tu proyecto, como script

Copia la plantilla [`plantilla-pipeline/pipeline_proyecto.py`](./plantilla-pipeline/pipeline_proyecto.py) a `psets/proyecto/modelado/`, al lado de tu notebook de features. Desde la próxima sesión, tus notebooks de modelos importan este archivo en vez de copiar su código:

```python
from pipeline_proyecto import cargar_y_dividir, construir_preparacion
```

### Paso 1: pasa tus features a `agregar_features` (5 minutos)

Copia de tu notebook de la sesión pasada solo las líneas que construyen tus 2 features, dentro de la función `agregar_features`. Sin gráficos, sin `print` y sin las celdas que usaste para probar ideas: esas se quedan en el notebook, como evidencia de por qué elegiste cada feature.

### Paso 2: clasifica tus columnas (5 minutos)

Escribe qué columnas son numéricas, cuáles categóricas y cuáles ya están listas, y cuál es el objetivo. Deja fuera toda columna que no exista al momento de predecir.

Objetivo: `units`. Numéricas: `sell_price`, `units_lag_7`, `units_media_28`. Categóricas: `dept_id`, `wday`, `month`. Ya listas: `is_snap`, `is_event_day`, `is_weekend`. Fuera: `revenue` (se calcula con el objetivo), `_loaded_at`, `week_idx` y las demás columnas que no existen al predecir.

### Paso 3: decide cómo dividir (5 minutos)

¿Tu modelo predice el futuro a partir de filas con fecha? Si sí, divide por fecha dentro de `cargar_y_dividir`; si no, al azar. Justifica.

Por fecha: el modelo predice el futuro a partir del pasado, así que las últimas 8 semanas (56 días) son la prueba y todo lo anterior el entrenamiento. Una división al azar mezclaría días vecinos del mismo producto entre entrenamiento y prueba y daría una evaluación demasiado optimista.

### Paso 4: corre el script (10 minutos)

Desde una terminal, en `psets/proyecto/modelado/`:

```
python3 pipeline_proyecto.py
```

Si corre de principio a fin en una terminal nueva, sin el notebook abierto, otro código ya lo puede importar. Anota la forma de los conjuntos de entrenamiento y prueba ya preparados, y la lista de columnas que produce.

`python3 pipeline_proyecto.py` corre de principio a fin (unos 10 segundos) y imprime: `Entrenamiento: (4532151, 32) Prueba: (170744, 32)` y las 32 columnas: `numericas__sell_price`, `numericas__units_lag_7`, `numericas__units_media_28`, 7 de `dept_id`, 7 de `wday`, 12 de `month`, `ya_listas__is_snap`, `ya_listas__is_event_day`, `ya_listas__is_weekend`.

## Antes de la próxima sesión

**Lectura:** ["Ensembles in Machine Learning"](https://towardsdatascience.com/ensembles-in-machine-learning-9128215629d1/), Towards Data Science.

Ya tienes los datos listos para entrenar. Si entrenas dos modelos sobre el mismo conjunto y uno da un error mucho menor en entrenamiento que en prueba, ¿qué le está pasando?

Se está sobreajustando: aprendió el ruido y los detalles de los datos de entrenamiento (casi memoriza las filas) y no generaliza a datos nuevos, por eso el error de prueba es mucho mayor.
