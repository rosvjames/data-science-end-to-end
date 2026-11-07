# Semana 6, Sesión 2: Procesamiento en tiempo real: ¿lo necesita el proyecto?

> Objetivo de la sesión: decidir si tu proyecto necesita procesamiento en tiempo real, y producir/consumir un flujo simple de eventos con una herramienta de streaming.

**Lectura previa de esta sesión:** ["Introduction to Streaming for Data Scientists"](https://huyenchip.com/2022/08/03/stream-processing-for-data-scientists.html), Chip Huyen.

**Referencia de esta sesión:** ["Batch or Stream? The Eternal Data Processing Dilemma" (Towards Data Science)](https://towardsdatascience.com/batch-or-stream-the-ethernal-data-processing-dilemma/). Este laboratorio usa Redpanda en vez de Apache Kafka con Zookeeper: un solo binario que habla el mismo protocolo de red que Kafka, así que cualquier cliente de Kafka (incluida la librería de Python de este laboratorio) se conecta sin cambios. Es el mismo criterio que ya usó este curso con DuckDB en vez de BigQuery (Semana 5): la herramienta real de la industria es la referencia, y el laboratorio usa la alternativa más simple de levantar en una sola laptop sin perder compatibilidad de protocolo. La misma edición de Data Engineering Zoomcamp que ya sirve de referencia a este curso usa Redpanda en su propio módulo de streaming.

## Requisitos antes de esta sesión

1. **Docker y Docker Compose**, los mismos de la Semana 3.
2. **El cliente de Python para Kafka (`kafka-python`):** ya viene en el Codespace. En tu laptop, instálalo con `pip install -r requirements.txt` desde la raíz del repositorio.
3. Levanta Redpanda desde este laboratorio:
   ```
   docker compose up -d
   ```
   El archivo [`starter/docker-compose.yml`](./starter/docker-compose.yml) levanta un solo broker de Redpanda, escuchando en el puerto `9092`, el mismo puerto estándar de Kafka. Verifica que el contenedor arrancó con `docker compose ps`.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué gana un sistema al procesar eventos uno por uno o en microlotes, frente a esperar y procesarlos todos juntos?**

Reacciona con baja latencia: cada evento se procesa al llegar (o en micro-lotes muy cortos), en vez de esperar a juntar todos; sirve cuando el valor del dato se pierde rápido. _(general, sin leer el artículo)_

**El artículo advierte que streaming no es gratis: agrega complejidad operativa real. ¿Qué tipo de complejidad menciona, comparado con un job de batch?**

Complejidad operativa: mantener servicios siempre encendidos (broker, procesadores), manejar fallas y reintentos, el orden y la duplicación de eventos, el estado y el monitoreo continuo; un batch corre, termina y se puede repetir. _(general, sin leer el artículo)_

## Caso de apertura

Un compañero de clase construye un sistema de recomendación de productos y quiere que se actualice apenas un cliente hace clic en algo. Otro construye un modelo que predice el precio de una casa a partir de datos que se publican una vez al mes. ¿Cuál de los dos proyectos se beneficia de procesar los datos en tiempo real, y cuál no gana nada haciéndolo?

El del sistema de recomendación se beneficia de tiempo real: debe reaccionar al clic apenas ocurre. El de la casa no gana nada: sus datos cambian una vez al mes, así que un batch mensual basta.

## Ejercicio 1: producir y consumir pedidos

Archivos: [`starter/ejercicio1_productor.py`](./starter/ejercicio1_productor.py), que arma 10 pedidos, y [`starter/ejercicio1_consumidor.py`](./starter/ejercicio1_consumidor.py), que los lee del tópico `pedidos` y los cuenta por categoría. Los dos ya corren contra Redpanda, pero tienen 4 `TODO` entre los dos. Córrelos en orden antes de tocar nada:

```
cd laboratorios/semana-06-sesion-02/starter
python3 ejercicio1_productor.py
python3 ejercicio1_consumidor.py
```

**Respuesta 1 (TODO 1), antes de ver la solución:** el productor imprimió los 10 eventos y el consumidor no recibió ninguno. ¿Qué le falta al productor?

Le falta publicar: solo armaba y mostraba los eventos. Hay que enviarlos con `productor.send("pedidos", value=evento)`.

**Respuesta 2 (TODO 2):** con el TODO 1 resuelto, el consumidor sigue sin recibir nada si lo corres después del productor, pero sí los recibe si ya estaba corriendo cuando el productor publicó. ¿Por qué?

Sin `auto_offset_reset="earliest"` el consumidor empieza en el final del tópico (`latest`) y solo ve los mensajes que lleguen después de arrancar. Con `earliest` empieza desde el primer evento guardado.

**Respuesta 3 (TODO 3):** ahora el consumidor imprime `b'{"id_pedido": 1, ...}'`. ¿Qué dos pasos de `serializar_evento` tiene que deshacer `deserializar_evento`, y en qué orden?

Dos pasos, en orden inverso: el productor hace `json.dumps` (diccionario a texto) y `.encode("utf-8")` (texto a bytes). El consumidor debe primero `.decode("utf-8")` (bytes a texto) y después `json.loads` (texto a diccionario).

**Respuesta 4 (TODO 4):** si corres el consumidor una segunda vez, ¿vuelve a mostrar los 10 eventos? Y si corres el productor otra vez, ¿el tópico queda con 10 o con 20?

Sí, vuelve a mostrar los 10: sin `group_id` no se guarda el punto donde quedó, y con `earliest` empieza otra vez desde el principio. El tópico queda con 20 si se corre otro productor: Kafka guarda los eventos y no se borran al leerlos; solo se agregan. _(Lo deduje del comportamiento; no repetí las corridas.)_

**Lo que confirmó la salida, TODO por TODO:**

Productor: 10 eventos publicados. Consumidor: recibió los 10 y el resumen final fue `{'hogar': 4, 'ropa': 3, 'electronica': 3}`. Lo corrí contra Redpanda en Docker.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: alertas de temperatura

Solo o en pareja. Archivos: [`starter/ejercicio2_productor.py`](./starter/ejercicio2_productor.py), que arma 8 lecturas de tres sensores, y [`starter/ejercicio2_consumidor.py`](./starter/ejercicio2_consumidor.py), que las lee del tópico `lecturas`. Son los mismos cuatro pasos del Ejercicio 1, más uno nuevo (TODO 5): una alerta cuando la temperatura pasa de 30 grados. Al final, el consumidor imprime una comprobación por TODO: complétalos hasta que todas digan `OK`.

```
python3 ejercicio2_productor.py
python3 ejercicio2_consumidor.py
```

**Respuesta 1:** ¿cuántas alertas aparecieron, de qué sensor, y en qué momento las imprimió el consumidor: al final, o a medida que llegaba cada lectura?

2 alertas, las dos del sensor `techo` (31.5 y 33.0 grados). El consumidor las imprime a medida que llega cada lectura, dentro del ciclo, no al final.

**Respuesta 2:** si el productor corriera todo el día enviando una lectura por minuto, ¿en qué cambiaría tu consumidor? ¿Seguiría teniendo sentido `consumer_timeout_ms`?

Sería un consumidor que corre sin parar y procesa cada lectura cuando llega; `consumer_timeout_ms` (que termina el programa tras 10 segundos sin eventos) ya no tendría sentido, porque entre una lectura y otra pasa un minuto y el consumidor se cerraría.

**Si terminas antes:** abre dos terminales y corre el consumidor del Ejercicio 2 en las dos al mismo tiempo, y después el productor. ¿Las dos reciben las 8 lecturas, o se las reparten? Compáralo con tu voto del ConcepTest.

Sin `group_id` (el valor por defecto), cada consumidor es independiente y las dos terminales reciben las 8 lecturas. Si compartieran un `group_id` se repartirían las particiones (y con una sola partición, solo uno recibiría). _(No lo probé con dos terminales; es lo que se deduce de cómo funciona.)_

## Ejercicio 3: tu propio proyecto, ¿streaming o batch?

Aplica las dos preguntas que decidieron el caso de apertura a tu propio proyecto, y produce/consume al menos un evento representativo de tu proyecto con Redpanda. Parte de la plantilla [`plantilla-kafka/`](./plantilla-kafka/), que trae los `TODO` marcados en `productor.py` y `consumidor.py` en vez del código en blanco: copia los dos archivos a `psets/proyecto/procesamiento/` y complétalos ahí.

### Paso 1: responde las dos preguntas de decisión para tu proyecto (5 minutos)

¿La decisión que tu proyecto habilita pierde valor si se toma con datos de hace una hora, un día o una semana? ¿Los datos de tu proyecto llegan de forma continua e impredecible, o en bloques ya definidos?

Si la decisión pierde valor en minutos o si los datos llegan continuos e impredecibles, conviene streaming; si las ventas llegan por bloques diarios y el modelo predice el día siguiente, basta batch. Mi proyecto (M5: ventas diarias de CA_1) es batch: la decisión de reposición se toma una vez al día y los datos se cierran por día. Aun así produje eventos de ventas como ejercicio.

### Paso 2: escribe tu productor (7 minutos)

Reemplaza el tópico y los eventos de ejemplo por al menos un evento representativo de tu propio proyecto.

Tópico `ventas_m5`; publiqué 6 eventos de venta (`fecha`, `item_id`, `dept_id`, `units`, `sell_price`, `is_snap`), uno de ellos atípico (15 unidades). Está en `psets/proyecto/procesamiento/productor.py`.

### Paso 3: escribe tu consumidor y confirma que recibe lo publicado (8 minutos)

El consumidor recibió los 6 eventos, sumó las unidades por departamento (`{'FOODS_3': 21, 'HOUSEHOLD_1': 1, 'HOBBIES_1': 3, 'FOODS_2': 2}`) y avisó de la venta atípica de `FOODS_3_090` (15 unidades). Lo corrí contra Redpanda en Docker.

## Al terminar

Apaga Redpanda desde `starter/`:

```
docker compose down
```

Este broker no tiene volumen: al apagarlo se pierden los tópicos y los mensajes que produjiste. Para el laboratorio integrador de la Semana 7 no los necesitas; si tu proyecto usa streaming, lo vuelves a levantar con `docker compose up -d` y tu productor genera los eventos otra vez.

## Antes de la próxima sesión

Ya decidiste si tu proyecto necesita streaming, y produjiste/consumiste tu primer flujo de eventos.

Pregunta: llevas cuatro semanas construyendo piezas sueltas del pipeline de tu proyecto (contenedor, infraestructura, orquestación, calidad, warehouse, modelado, batch, streaming). ¿Qué falta para que todas esas piezas corran juntas, de principio a fin, sin que tengas que ejecutarlas una por una a mano?

Falta un orquestador que las conecte en un solo flujo con dependencias, horarios, reintentos y alertas (Kestra), con todo en contenedores, y pruebas de integración continua que verifiquen que las piezas funcionan juntas de principio a fin.
