# Semana 7, Sesión 2: Repaso Medio Semestre

> Objetivo de la sesión: consolidar los conceptos de formulación de problemas e infraestructura de datos mediante preguntas dirigidas por ustedes mismos, y relacionar el concepto de contrato de datos con el pipeline de su propio proyecto.

**Lectura previa de esta sesión:** ["What Is a Data Contract?"](https://www.ibm.com/think/topics/data-contract), IBM Think.

**Referencia:** ["From Monolith to Contract-Driven Data Mesh"](https://towardsdatascience.com/from-monolith-to-contract-driven-data-mesh/), Towards Data Science.

Esta sesión no tiene un ejercicio de código nuevo. Es una guía de repaso: la llenas antes de la sesión, con tus propias preguntas sin resolver, y la usas durante la sesión para seguir el turno de preguntas y la discusión del cierre.

## Antes de la sesión: tu pregunta por categoría

Para cada categoría, escribe la pregunta concreta que todavía no puedes responder con seguridad, no una duda general. "No entendí bien Kestra" no se puede resolver en dos minutos; "no sé por qué mi flow no espera a que Postgres esté listo" sí.

Si una categoría ya te quedó completamente clara, escribe "sin pregunta" y seguimos a la siguiente en clase.

**Formulación de problemas (Semanas 1-2):**

¿Cómo defino el costo de subestimar frente a sobreestimar la demanda, si no tengo los márgenes ni la merma reales de la tienda?

**Contenedores e infraestructura como código (Semana 3):**

Con un archivo de 150 MB, ¿conviene montarlo por volumen o incluirlo en la imagen? (Usé volumen: la imagen queda chica y los datos no se versionan.)

**Orquestación y calidad de datos (Semana 4):**

¿Cómo hace Kestra para usar una imagen local, sin registro, y mantener su tag actualizado cuando la reconstruyo?

**Warehouse y modelado analítico (Semana 5):**

En dbt, `unique` solo mira una columna: para una clave compuesta (producto y día), ¿es mejor una clave sintética en staging o una prueba de combinación única?

**Procesamiento batch y streaming (Semana 6):**

Si DuckDB resolvió la misma agregación sobre 5.9 millones de filas en segundos, ¿cuándo se justifica de verdad Spark?

**Integración de principio a fin (Semana 7, Sesión 1):**

¿Cómo verifico que cada etapa lee exactamente lo que produjo la anterior, y cómo corro todo encadenado sin ejecutar etapa por etapa a mano?

## Durante el turno de preguntas

Espacio para anotar, de las preguntas de tus compañeros, la que más te sirvió a ti también (la que resolvió algo que no habías anotado como tu propia pregunta):

_(tu respuesta)_

## Discusión complementaria, contrato de datos

**Antes de la discusión, a partir de la lectura:** según el artículo de IBM, ¿qué distingue a un contrato de datos de la documentación tradicional de un esquema?

Un contrato de datos es un acuerdo formal y verificable entre quien produce los datos y quien los consume: define esquema, significado de las columnas, calidad esperada, frescura y responsables, y se puede hacer cumplir. La documentación de un esquema solo describe cómo son los datos hoy, y nada obliga a mantenerla o a respetarla. _(general, sin leer el artículo)_

**Pregunta de la discusión:** ¿qué garantiza un contrato de datos entre el equipo que produce y el equipo que consume un pipeline, que una prueba de dbt corriendo en silencio no garantiza por sí sola?

Garantiza un compromiso entre las dos partes: qué significa cada columna, cada cuánto llega, qué cambios se avisan antes (versionado) y quién responde. Una prueba de dbt en silencio solo detecta, del lado del consumidor, que algo se rompió, y después: no previene el cambio, no dice qué significaba el dato ni quién debe arreglarlo.

**Después de la discusión, ¿qué agregarías o cambiarías de tu respuesta?**

_(tu respuesta)_

**Aplicado a tu propio proyecto:** de las pruebas `unique`/`not_null` que ya escribiste en el `schema.yml` de dbt (Semana 5, Sesión 2), elige una columna de tu warehouse cuyo significado exacto no queda claro solo con el nombre de la columna (¿una fecha en qué huso horario? ¿un monto con o sin impuesto?). Escribe, en una frase, la aclaración que le harías a alguien que fuera a consumir esa tabla sin haber visto tu código.

En `ventas_ca1`, la columna `units` (unidades vendidas del producto en la tienda ese día): un 0 no siempre significa "no hubo demanda"; puede ser un quiebre de stock (entre 9.5% y 26.5% de los ceros, según el criterio), y las filas anteriores al lanzamiento del producto también tienen 0 sin que el producto existiera (`is_pre_launch`).

## Antes de la próxima sesión

La próxima sesión es la Evaluación Medio Semestre. Repasa las seis categorías del mapa de repaso de esta sesión, con especial atención a las preguntas que anotaste arriba.
