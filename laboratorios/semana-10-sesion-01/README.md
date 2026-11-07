# Semana 10, Sesión 1: Entrenamiento y comparación de modelos I: línea base y ensamblajes

> Objetivo de la sesión: entrenar un modelo de línea base y un modelo de ensamblaje sobre los datos preparados de tu proyecto, y aplicar regularización cuando el modelo se sobreajusta, sin derivar la matemática del descenso de gradiente.

**Lectura previa de esta sesión:** ["Ensembles in Machine Learning"](https://towardsdatascience.com/ensembles-in-machine-learning-9128215629d1/), Towards Data Science.

**Referencia de esta sesión:** [Ensemble methods (documentación oficial de scikit-learn)](https://scikit-learn.org/stable/modules/ensemble.html).

## Requisitos antes de esta sesión

Nada nuevo que instalar: todo lo de hoy está en scikit-learn, que ya usaste la sesión pasada. Ten a mano el script `pipeline_proyecto.py` de tu proyecto, de la Semana 9, Sesión 2.

Los laboratorios de hoy son notebooks: entrenar y comparar modelos es experimentar, y en un notebook vuelves a correr solo el modelo que cambiaste, sin reentrenar los demás. La preparación no se copia en el notebook: se importa del script, para que todos los modelos usen exactamente la misma.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué es un ensamblaje, y en qué se diferencian bagging y boosting en la forma de combinar sus modelos?**

Un ensamblaje combina las predicciones de muchos modelos para obtener una mejor que la de cualquiera por separado. En bagging (como el bosque aleatorio) cada modelo se entrena en paralelo e independiente, con una muestra distinta de los datos, y sus predicciones se promedian (o se vota), lo que reduce la varianza. En boosting (como gradient boosting) los modelos se entrenan en secuencia y cada uno intenta corregir los errores del anterior, lo que reduce el sesgo.

**¿Por qué un promedio de muchos árboles puede equivocarse menos que el mejor de esos árboles por separado?**

Porque cada árbol se equivoca de forma distinta: sus errores por sobreajuste a su muestra no son los mismos. Al promediar, los errores que no coinciden se cancelan parcialmente y queda la señal que todos comparten, así que la varianza baja. El mejor árbol solo puede ser tan bueno como su propia muestra; el promedio de árboles diversos (entrenados con muestras y columnas distintas) generaliza mejor.

## Pregunta de apertura

Ya tienes los datos listos para entrenar. Si entrenas dos modelos sobre el mismo conjunto y uno da un error mucho menor en entrenamiento que en prueba, ¿qué le está pasando?

Se está sobreajustando: aprendió el ruido y los detalles del conjunto de entrenamiento (casi memorizó las filas) y no generaliza a datos nuevos. El error de entrenamiento engaña, por eso se mide siempre en un conjunto de prueba aparte.

## Ejercicio 1: línea base, un árbol y un bosque

Notebook: [`starter/ejercicio1_linea_base_y_ensamblaje.ipynb`](./starter/ejercicio1_linea_base_y_ensamblaje.ipynb), sobre [`starter/viajes_features.csv`](./starter/viajes_features.csv), el mismo de la sesión pasada. La preparación de la Semana 9 está en [`starter/preparacion_taxis.py`](./starter/preparacion_taxis.py) y el notebook la importa. Ya trae una función `evaluar` que entrena cada modelo, mide el error absoluto medio en entrenamiento y en prueba, y lo registra en una tabla. Los 4 `TODO` son los modelos, cada uno en su celda. Córrelo completo una vez antes de tocar nada (**Run All**).

**Respuesta 1 (TODO 1):** la línea base predice siempre la mediana de la tarifa. ¿Cuánto esperas que se equivoque en promedio? ¿Para qué sirve un modelo que no usa ninguna columna?

Esperaba que se equivocara por unos 13 dólares en promedio, porque predice la misma tarifa para todos los viajes y las tarifas varían mucho (hay hasta viajes de tarifa fija de 70). Sirve como piso de referencia: un modelo que no mejora a la línea base no está aprendiendo nada útil de las columnas. Salió 13.20 en entrenamiento y 12.53 en prueba.

**Respuesta 2 (TODO 2):** un árbol sin límite puede seguir partiendo los datos hasta dejar un viaje por hoja. ¿Qué error esperas en entrenamiento, y qué esperas en prueba?

En entrenamiento esperaba un error casi cero, porque con una hoja por viaje el árbol memoriza cada tarifa; en prueba, un error bastante mayor, porque esas reglas tan específicas no se repiten en viajes nuevos. Salió 0.0029 en entrenamiento y 1.7017 en prueba.

**Respuesta 3 (TODO 3 y 4):** ¿qué esperas que pase con la brecha entre entrenamiento y prueba al limitar la profundidad? ¿Y con 200 árboles promediados?

Al limitar la profundidad esperaba que la brecha se achicara (el árbol ya no puede memorizar), aunque el error de entrenamiento sube; así fue: de 1.70 a 0.26. Con 200 árboles promediados esperaba un error de prueba menor y una brecha más chica que la del árbol sin límite, pero no tan chica como la del árbol limitado, porque cada árbol sigue siendo profundo. La brecha fue 0.82 y el error de prueba 1.30.

**Lo que confirmó la tabla, TODO por TODO:**

| Modelo | Entrenamiento | Prueba | Brecha |
|---|---|---|---|
| Línea base (mediana) | 13.1998 | 12.5308 | −0.6690 |
| Árbol sin límite | 0.0029 | 1.7017 | 1.6988 |
| Árbol max_depth=8 | 1.0098 | 1.2728 | 0.2630 |
| Bosque de 200 árboles | 0.4743 | 1.2989 | 0.8245 |

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: regularizar una regresión que se sobreajusta

Solo o en pareja. Notebook: [`starter/ejercicio2_regularizacion.ipynb`](./starter/ejercicio2_regularizacion.ipynb), sobre el mismo `viajes_features.csv` y con la misma preparación importada. Mismo esqueleto del Ejercicio 1; `evaluar` acepta además `grado_interacciones=3`, que agrega como columnas todos los productos entre columnas hasta grado 3. Los pasos 1 a 3 tienen `TODO`; los pasos 4 y 5 solo tienen la comprobación. Complétalos hasta que todas digan `OK`.

**Respuesta 1:** ¿cuántas columnas recibe la regresión con interacciones de grado 3, y cuántas filas de entrenamiento hay? ¿Qué tiene que ver esa comparación con el error en prueba que obtuviste?

Recibe 3275 columnas y hay 2380 filas de entrenamiento: más columnas que filas, así que la regresión puede ajustar exactamente el entrenamiento (error 0.88) y memoriza el ruido. En prueba el error fue de unos 287 millones de dólares, absurdamente peor que la línea base (12.53), con una brecha de la misma magnitud. El modelo es numéricamente inestable (ajusta con coeficientes enormes sobre columnas casi colineales), así que ese valor exacto cambia entre versiones de las librerías; lo importante es que es catastrófico.

**Respuesta 2:** ¿qué cambió entre `lineal grado 3` y `ridge grado 3` en el error de entrenamiento, y qué cambió en el de prueba? ¿Por qué Ridge empeora un poco en entrenamiento?

El error de entrenamiento subió un poco, de 0.8837 a 1.0272, y el de prueba bajó de 287 651 195 a 1.32. Ridge penaliza los coeficientes grandes, así que ya no puede ajustar exactamente cada punto de entrenamiento, y por eso empeora un poco ahí; a cambio generaliza mucho mejor.

**Respuesta 3:** ¿qué modelo quedó mejor en prueba? ¿Cuánto mejor que la línea base?

El gradient boosting, con 1.2754 de error en prueba (el ridge de grado 3 queda muy cerca, con 1.321). Frente a la línea base (12.53) reduce el error en unos 11.3 dólares, cerca del 90%.

**Si terminas antes:** la brecha de la línea base es negativa (se equivoca menos en prueba que en entrenamiento). ¿Cómo puede pasar eso con un modelo que no aprende nada?

Porque la línea base no aprende nada del conjunto de entrenamiento salvo la mediana: su error depende solo de qué viajes caen en cada conjunto. Los 595 viajes de prueba, por cómo cayó la división al azar, quedaron en promedio algo más cerca de la mediana que los 2380 de entrenamiento, y la diferencia de −0.67 es solo efecto de ese reparto, no aprendizaje.

## Ejercicio 3: los primeros modelos de tu proyecto

Usa tu pipeline de la Semana 9, Sesión 2, con la misma división de entrenamiento y prueba. Esta vez no hay plantilla: escribe el notebook tú.

### Entregable 1: `modelos_proyecto.ipynb`

Un notebook, en la misma carpeta que tu `pipeline_proyecto.py` (`psets/proyecto/modelado/`), que importe de ahí la preparación y la división (`from pipeline_proyecto import cargar_y_dividir, construir_preparacion`) en vez de copiarlas, y que entrene:

- Una línea base. Elige la que corresponde a tu problema y justifícala abajo: `DummyRegressor` o `DummyClassifier`, o una regla del dominio (por ejemplo, "mañana igual que hoy" si predices una serie en el tiempo).
- Un modelo lineal (`Ridge` si es regresión, `LogisticRegression` si es clasificación), con la regularización que haga falta.
- Un ensamblaje (`RandomForestRegressor`, `GradientBoostingRegressor` o sus versiones `Classifier`).

### Entregable 2: `resultados_proyecto.csv`

Una fila por modelo, con la métrica de tu proyecto en entrenamiento y en prueba, la brecha y los segundos de entrenamiento, escrita por el notebook. Antes de hacer commit, reinicia el kernel y corre todo: la tabla tiene que salir de una corrida completa, no de celdas corridas en momentos distintos.

### Entregable 3: respuestas

Proyecto M5 (CA_1), predecir las unidades vendidas de un item al día siguiente. Notebook: `psets/proyecto/modelado/modelos_proyecto.ipynb`; tabla: `psets/proyecto/modelado/resultados_proyecto.csv`. MAE en unidades, división por fecha, entrenamiento con 200 000 filas.

| Modelo | Entrenamiento | Prueba | Brecha | Segundos |
|---|---|---|---|---|
| Línea base: mediana constante | 1.6441 | 1.5344 | −0.1097 | 0.15 |
| Línea base: media de 28 días | 1.1793 | 1.1082 | −0.0711 | — |
| Ridge alpha=1 | 1.1921 | 1.1190 | −0.0731 | 0.16 |
| Ridge alpha=1000 | 1.1915 | 1.1189 | −0.0726 | 0.16 |
| Bosque sin límite | 0.4529 | 1.1630 | 0.7100 | 7.96 |
| Bosque min_samples_leaf=50 | 1.1233 | 1.0907 | −0.0326 | 5.77 |
| Gradient boosting | 1.1470 | 1.0895 | −0.0575 | 15.95 |

**¿Cuál es tu línea base, y por qué esa y no otra?**

La media de las ventas de los 28 días previos del item. Es la regla que un encargado de tienda aplicaría sin modelo (el promedio reciente) y es una referencia mucho más exigente que una constante: la mediana constante da 1.53 de MAE y la media de 28 días 1.11. Si un modelo no la mejora, no vale la pena mantenerlo. Reporto también la mediana constante como piso.

**¿Alguno de tus modelos se sobreajusta? Muestra la evidencia con números de tu tabla.**

Sí, el bosque sin límite: error de 0.4529 en entrenamiento y 1.1630 en prueba, brecha de 0.71, y en prueba es peor que la línea base (1.1082). Los demás tienen brecha negativa o casi cero (−0.03 a −0.07): el periodo de prueba (últimas 8 semanas) es algo más fácil de predecir que el de entrenamiento, como le pasaba a la línea base, así que no es señal de sobreajuste.

**¿Qué regularización aplicaste (o por qué no hizo falta), y qué cambió en la tabla?**

Al bosque le puse `min_samples_leaf=50` (cada hoja debe tener al menos 50 filas). Eso bajó el error de prueba de 1.1630 a 1.0907 y la brecha de 0.71 a −0.03, aunque el error de entrenamiento subió de 0.45 a 1.12. Al Ridge no le hizo falta: solo hay 32 columnas y 200 000 filas, y alpha=1 y alpha=1000 dan prácticamente el mismo resultado (1.1190 y 1.1189). El gradient boosting corre con sus valores por defecto, que ya tienen árboles poco profundos (max_depth=3).

**¿Cuánto mejora tu mejor modelo a la línea base?**

El mejor es el gradient boosting con 1.0895 de MAE en prueba (el bosque regularizado queda a 0.001, con 1.0907). Frente a la mediana constante (1.5344) mejora un 29%, pero frente a la línea base exigente (media de 28 días, 1.1082) solo 0.019 unidades, un 1.7%. Casi toda la señal ya estaba en `units_media_28`.

## Antes de la próxima sesión

**Lectura:** ["Machine Learning vs LLM: Differences, Applications & Impact"](https://www.neuralconcept.com/post/ml-vs-llm-key-differences-applications-engineering-impact), Neural Concept.

Para estimar la tarifa de un viaje, podrías entrenar un ensamblaje, entrenar una red neuronal o escribirle a un LLM los datos del viaje y pedirle un número. ¿Qué tendrías que medir de cada opción, además del error, para decidir cuál usar en la app de taxis?

Además del error: el costo de entrenar y de cada predicción, la latencia, si da el mismo número ante la misma entrada (reproducibilidad), si puedo explicar por qué dio ese número, cómo se comporta en casos raros (tarifa fija, rutas poco vistas) y el esfuerzo de mantenerlo (reentrenar, versionar, depender de un proveedor).
