# Semana 5, Sesión 2: Modelado analítico (analytics engineering)

> Objetivo de la sesión: construir un modelo de datos en capas (staging, intermedia, marts) con pruebas y documentación para los datos de tu proyecto.

**Lectura previa de esta sesión:** ["What is analytics engineering?"](https://www.getdbt.com/blog/what-is-analytics-engineering), dbt Labs.

**Referencia de esta sesión:** [dbt, documentación oficial](https://docs.getdbt.com/docs/introduction). Este laboratorio usa `dbt-duckdb`, el adaptador que conecta dbt al mismo warehouse de DuckDB que construiste la sesión pasada: dbt corre igual de local que DuckDB, sin ningún servicio ni cuenta adicional.

## Requisitos antes de esta sesión

1. **El warehouse de DuckDB de la Sesión 1**, con los datos de tu proyecto ya cargados (el archivo `.duckdb` del Ejercicio 3 de la sesión pasada).
2. **dbt con el adaptador de DuckDB:** ya viene en el Codespace. En tu laptop, instálalo con `pip install -r requirements.txt` desde la raíz del repositorio. Verifica con:
   ```
   dbt --version
   ```
   Deberías ver `duckdb` listado en la sección de plugins.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué hace un analytics engineer que no hace ni un ingeniero de datos puro ni un analista puro?**

Hace de puente entre ambos: toma datos ya cargados por el ingeniero de datos y los transforma con SQL, con prácticas de ingeniería (versionado, pruebas, documentación), para dejar tablas listas que el analista consume. _(general, sin leer el artículo)_

**El artículo describe el flujo de trabajo de dbt (escribir SQL, dbt lo convierte en tablas o vistas). ¿Qué gana ese SQL por vivir dentro de un proyecto de dbt en vez de pegarse directo en una consola de SQL?**

Gana versionado en git, modelos que dependen unos de otros con `ref()` (dbt resuelve el orden), pruebas automáticas, documentación y reproducibilidad: cualquiera lo corre igual, en vez de una consulta pegada a mano que nadie revisa. _(general, sin leer el artículo)_

## Pregunta de apertura

Imagina un solo archivo SQL de 200 líneas: limpia los datos crudos, calcula columnas de negocio, une varias tablas y agrega el resultado final, todo en una sola consulta con subconsultas anidadas. Funciona. ¿Por qué no dejarlo así?

Porque es difícil de leer, probar, reutilizar y mantener: si algo falla no se sabe en qué parte, no se puede probar cada paso y cualquier cambio obliga a tocar todo. Separado en capas (staging, intermedia, marts), cada una se entiende y se prueba por separado.

## Ejercicio 1: pedidos por ciudad, en tres capas

Carpeta: [`starter/ejercicio1/`](./starter/ejercicio1/), un proyecto de dbt completo sobre las mismas tablas de la Sesión 1. Ya corre de principio a fin, pero cada capa tiene un `TODO`: staging con `select *`, sin prueba sobre `stg_pedidos`, un modelo intermedio que lee las tablas crudas por su nombre, y un mart sin agregar. Córrelo una vez antes de tocar nada:

```
cd laboratorios/semana-05-sesion-02/starter/ejercicio1
python3 cargar_raw.py
dbt run --profiles-dir .
dbt test --profiles-dir .
```

**Respuesta 1 (TODO 1), antes de ver la solución:** si `stg_pedidos` solo selecciona columnas de `raw_pedidos`, sin ningún cálculo, ¿qué sentido tiene un modelo aparte en vez de consultar `raw_pedidos` directamente?

Aísla el contacto con la tabla cruda en un solo lugar: si la fuente cambia de nombre o de tipo, se arregla ahí y el resto del proyecto no se entera. Es también el sitio natural para limpiar, renombrar y probar la tabla.

**Respuesta 2 (TODO 2):** ¿sobre qué columna de `stg_pedidos` pondrías la prueba `unique`? ¿Qué tendría que pasar en `pedidos.csv` para que falle?

Sobre `id_pedido`, que identifica cada pedido: `unique` falla si `pedidos.csv` trae un `id_pedido` repetido, y `not_null` si alguno viene vacío.

**Respuesta 3 (TODO 3):** mira el orden en que `dbt run` construyó los modelos. ¿Por qué `int_pedidos_con_cliente` salió primero, antes que los modelos de staging de los que depende? ¿Qué cambia con `ref()`?

Porque `int_pedidos_con_cliente` leía las tablas crudas por su nombre y dbt no sabía que dependía de staging: sin dependencias declaradas, los construye en orden alfabético. Con `ref('stg_...')` dbt arma el grafo y construye primero staging, luego el intermedio y al final el mart. _(El orden inicial lo deduje; no corrí el estado sin resolver.)_

**Respuesta 4 (TODO 4):** si mañana cambias cómo se calcula `monto_total` en el modelo intermedio, ¿tienes que tocar también el mart?

No: el mart lee el modelo intermedio con `ref()`, y el intermedio es donde está el cálculo. Al cambiar `monto_total` ahí y volver a correr `dbt run`, el mart se reconstruye con el nuevo cálculo.

**Lo que confirmó la salida, TODO por TODO:**

Orden final de `dbt run`: `stg_clientes`, `stg_pedidos`, `int_pedidos_con_cliente`, `marts_ventas_por_ciudad`; 4 pruebas pasan (`unique` y `not_null` de `id_cliente` e `id_pedido`). El mart da Quito 5 pedidos y 2 324.5, Guayaquil 3 y 994.5, Cuenca 2 y 126.0 (los mismos números del warehouse de la Sesión 1).

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: ventas por categoría, en tres capas

Solo o en pareja. Carpeta: [`starter/ejercicio2/`](./starter/ejercicio2/), las ventas y productos de la Sesión 1 (con una diferencia en `ventas.csv` que vas a encontrar con una prueba). Son las mismas cuatro capas del Ejercicio 1 (TODO 1 a 4), más uno nuevo (TODO 5). Después de cada cambio, corre:

```
python3 cargar_raw.py
dbt run --profiles-dir .
dbt test --profiles-dir .
python3 comprobar.py
```

`comprobar.py` imprime `OK` o `revisa` por cada TODO: complétalos hasta que todos digan `OK`.

**Respuesta 1:** ¿qué prueba falló primero, y qué fila de `ventas.csv` la hizo fallar?

Falló `unique_stg_ventas_id_venta`, por `id_venta` 4 (producto P1, 2026-04-02, 5 unidades), que aparece dos veces idéntica en `ventas.csv`.

**Respuesta 2 (TODO 5):** corregiste la causa en `stg_ventas`, no en `ventas.csv`. ¿Por qué ahí y no en el archivo, si el archivo es el que está mal?

Porque el archivo crudo es la fuente tal como llegó: no se edita (se perdería el rastro de lo que se recibió y la próxima carga volvería a traer el error). La corrección vive en el código (`select distinct` en `stg_ventas`), versionada y repetible, y la prueba `unique` vigila que la causa siga corregida.

**Si terminas antes:** sin el TODO 5, ¿cuánto daba el monto de papelería en el mart, y cuánto da después? ¿Qué habría pasado con ese número si nadie hubiera escrito la prueba?

Con la fila duplicada, papelería habría dado 122.0 (se contaba dos veces la venta de P1: 5 × 2.5 = 12.5); después da 109.5. Sin la prueba, nadie habría notado el error y el reporte habría salido con un monto inflado sin ningún aviso. _(El 122.0 lo calculé, no corrí el estado sin resolver.)_

## Ejercicio 3: modela en capas los datos de tu propio proyecto

Usa el mismo patrón de los Ejercicios 1 y 2 (staging, intermedia, marts), aplicado a la tabla que cargaste a tu warehouse en la Sesión 1. Parte de la plantilla [`plantilla-dbt/`](./plantilla-dbt/), que trae los `TODO` marcados en cada archivo en vez del proyecto en blanco: copia la carpeta completa a `psets/proyecto/warehouse/dbt/` y trabaja ahí, al lado del `.duckdb` de la Sesión 1.

### Paso 1: staging (7 minutos)

Renombra `models/staging/stg_TODO.sql` a `stg_<tu_tabla>.sql`, selecciona las columnas de tu tabla cruda, y agrega al menos una prueba (`unique` o `not_null`) en `schema.yml` sobre la columna que identifica cada fila.

Staging `stg_ventas_ca1` (columnas usadas, una `clave_item_dia` por producto y día, y `cast` de la fecha). Pruebas: `unique` y `not_null` sobre `clave_item_dia`, y `not_null` sobre `units`.

### Paso 2: intermedia y marts (13 minutos)

Renombra y completa `models/intermedia/int_TODO.sql` con una transformación o combinación de tablas de staging (usando `{{ ref(...) }}`), y `models/marts/marts_TODO.sql` con la agregación final que responda una pregunta real de tu proyecto.

`int_ventas_vendibles`: descarta las filas pre-lanzamiento (ceros sin precio) y agrega el mes y el ingreso. `marts_ventas_por_depto_mes`: unidades y proporción de ceros por departamento y mes, para saber qué se vende y cuánta de la serie son ceros. Está en `psets/proyecto/warehouse/dbt/`.

Corre y prueba tu proyecto:

```
dbt run --profiles-dir .
dbt test --profiles-dir .
```

`dbt run`: 3 modelos creados (2 vistas y 1 tabla, 455 filas en el mart). `dbt test`: 3 pruebas, todas pasan.

## Antes de la próxima sesión

Ya tienes tus datos organizados en capas, con pruebas que fallan si algo se rompe.

Pregunta: todo lo que hiciste hasta ahora (warehouse, capas, pruebas) asume que tus datos caben enteros en la memoria de tu computadora. ¿Qué pasa el día en que el historial completo de tu proyecto ya no cabe?

Hay que procesar los datos por partes o fuera de la memoria: motores distribuidos (como Spark) que reparten el trabajo en varios nodos, o almacenamiento y cómputo en la nube; una sola máquina deja de bastar.
