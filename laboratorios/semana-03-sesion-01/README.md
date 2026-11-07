# Semana 3, Sesión 1: Contenedores para pipelines de proyectos

> Objetivo de la sesión: empaquetar el entorno de trabajo de tu proyecto propio en una imagen de Docker reproducible, y explicar qué problema de "funciona en mi máquina" resuelve un contenedor.

**Lectura previa de esta sesión:** ["How Docker Can Help You Become a More Effective Data Scientist"](https://medium.com/data-science/how-docker-can-help-you-become-a-more-effective-data-scientist-7fc048ef91d5), Towards Data Science / Medium.

**Referencia de esta sesión:** [Data Engineering Zoomcamp, Módulo 1 (DataTalksClub)](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform).

## Requisitos antes de esta sesión

Abre el Codespace de tu fork (ver [Tu ambiente de desarrollo](../../README.md#tu-ambiente-de-desarrollo) en el README del repositorio): Docker ya viene instalado. Confirma que funciona corriendo `docker run hello-world` en la terminal. Si prefieres trabajar en tu laptop, instala [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows, Mac o Linux) y corre la misma verificación. Si tu proyecto necesita GPU o un ambiente que no corre bien en ninguna de las dos opciones, avísame antes de esta sesión.

El Codespace también es un contenedor, pero no reemplaza el Dockerfile que construyes hoy. El Codespace trae las herramientas del curso, iguales para todos. La imagen de tu proyecto trae solo lo que tu proyecto necesita para correr en cualquier máquina, incluida una que nunca abrió este repositorio.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué diferencia hay entre una imagen de Docker y un contenedor?**

La imagen es la plantilla de solo lectura (código, librerías y sistema); el contenedor es una instancia en ejecución de esa imagen. _(general, sin leer el artículo)_

**¿Qué captura Docker, además de las librerías de Python, que un `requirements.txt` por sí solo no captura?**

El sistema operativo, la versión de Python y sus librerías del sistema, y la configuración del entorno: `requirements.txt` solo lista paquetes de Python. _(general, sin leer el artículo)_

## Pregunta de apertura

¿Por qué un notebook que corre perfecto en mi laptop podría fallar por completo en la tuya, aunque ambos tengan el mismo código?

Porque "el mismo código" depende de un entorno distinto: otra versión de Python o de pandas, librerías del sistema, rutas o archivos que solo existen en una máquina.

## Ejercicio 1: la imagen de un script con pandas y datos

Carpeta: [`starter/ejercicio1/`](./starter/ejercicio1/). `procesar.py` lee `datos/ventas.csv` con pandas, imprime el total por producto y guarda `datos/resumen_ventas.csv`. El [`Dockerfile`](./starter/ejercicio1/Dockerfile) ya construye, pero tiene dos `TODO`. Constrúyelo y córrelo antes de tocar nada:

```
cd laboratorios/semana-03-sesion-01/starter/ejercicio1
docker build -t procesar-ventas .
docker run procesar-ventas
```

**Respuesta 1, antes de ver la solución:** el Dockerfile fija `python:3.11-slim` y no solo `python`. ¿Qué cambiaría en un año si dijera solo `python`?

Que la imagen cambiaría sola cuando salga una versión nueva de Python, y el mismo Dockerfile construiría un entorno distinto (y podría romper el código). Fijar `3.11-slim` hace la imagen reproducible.

**Respuesta 2 (TODO 1):** si cambias una línea de `procesar.py` y vuelves a construir, ¿qué pasos se repiten? ¿Cómo reordenarías las líneas para que `pip install` no se repita?

Se repiten el `pip install` y todo lo que va después, porque `COPY . .` cambia la capa. Se copia primero `requirements.txt`, luego `pip install`, y al final `COPY . .`: así un cambio de código solo repite el último paso.

**Respuesta 3 (TODO 2):** `docker run procesar-ventas` termina sin imprimir nada y sin error. ¿Qué le falta a la imagen?

El comando por defecto: sin `CMD` la imagen no sabe qué ejecutar y termina de inmediato. Faltaba `CMD ["python", "procesar.py"]`.

**Respuesta 4 (TODO 3, el comando de `docker run`):** con los TODO 1 y 2 resueltos, la imagen solo copia `procesar.py`. ¿Encuentra `datos/ventas.csv` al correr? Y si lo encontrara, ¿dónde quedaría `resumen_ventas.csv` cuando el contenedor termina?

No: la imagen solo copia `procesar.py`, así que `datos/ventas.csv` no existe adentro; hay que montarlo con `-v`. Y si lo encontrara, `resumen_ventas.csv` se escribiría dentro del contenedor y se perdería al terminar, salvo que haya un volumen.

**Lo que confirmó la salida, TODO por TODO:**

Dockerfile final: `FROM python:3.11-slim`, `WORKDIR /app`, `COPY requirements.txt .`, `RUN pip install --no-cache-dir -r requirements.txt`, `COPY . .`, `CMD ["python", "procesar.py"]`. Comando: `docker run --rm -v "$(pwd)/datos:/app/datos" procesar-ventas`. Lo que no esperaba: que sin `-v` no falle ni se vea el resumen en mi carpeta, porque el archivo queda dentro del contenedor.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: la imagen de un resumen de clientes

Solo o en pareja. Carpeta: [`starter/ejercicio2/`](./starter/ejercicio2/). `resumir_clientes.py` cuenta los clientes por ciudad y guarda `datos/clientes_por_ciudad.csv`; `contar_filas.py` guarda el total de clientes en `datos/conteo.txt`. Escribe el `Dockerfile` con el mismo patrón del Ejercicio 1 (TODO 1 a 3), y después:

- **TODO 4:** corre la imagen con un volumen para que `clientes_por_ciudad.csv` aparezca en tu carpeta `datos/`.
- **TODO 5:** corre `contar_filas.py` con la misma imagen, sin cambiar el Dockerfile ni volver a construir. Pista: lo que escribes después del nombre de la imagen en `docker run` reemplaza el `CMD`.

Revisa tu avance con:

```
bash comprobar.sh
```

**Respuesta 1:** ¿qué comando usaste en el TODO 5? ¿Qué significa, entonces, que `CMD` sea el comando "por defecto"?

Pasé lo que sigue de `docker run <imagen>` (`python contar_filas.py`): reemplaza el `CMD`. Entonces `CMD` es solo el comando por defecto, el que se usa si no se indica otro.

**Respuesta 2:** si borras `datos/clientes_por_ciudad.csv` de tu carpeta y corres la imagen otra vez sin `-v`, ¿qué pasa?

El contenedor vuelve a crear el archivo, pero dentro de su propio sistema de archivos: sin `-v` no aparece en mi carpeta `datos/` y se pierde al terminar.

**Si terminas antes:** `contar_filas.py` no usa pandas. ¿Valdría la pena una imagen aparte para él, sin `pip install`? ¿Qué ganarías y qué perderías?

Quizá sí: una imagen más chica y rápida de construir, sin pandas. Pero se tendrían dos imágenes que mantener y versionar; con una sola imagen basta cambiar el comando.

## Ejercicio 3: el Dockerfile de tu propio proyecto

Usa el mismo patrón de los Ejercicios 1 y 2, aplicado al ambiente de tu proyecto. Parte de la plantilla [`plantilla-dockerfile/Dockerfile`](./plantilla-dockerfile/Dockerfile), que trae los `TODO` marcados en vez del Dockerfile en blanco. Tu proyecto vive en [`psets/proyecto/`](../../psets/README.md) durante todo el semestre: copia la plantilla a la raíz de `psets/proyecto/` y trabaja ahí, con tu script de ingesta en `psets/proyecto/ingesta/`.

### Paso 1: identifica tus dependencias reales (5 minutos)

Lista las librerías externas que tu proyecto necesita (lo que normalmente instalarías con `pip install`). Si todavía no tienes un `requirements.txt`, créalo ahora con esa lista, en `psets/proyecto/`, al lado del Dockerfile. Fija la versión de cada librería (`pandas==2.2.2`, no solo `pandas`), como el `requirements.txt` de la raíz del repositorio: sin versión, la imagen que construyas en un mes puede traer una librería distinta de la que probaste hoy.

`pandas==2.2.2`, `scikit-learn==1.5.2` y `numpy==1.26.4` (en `psets/proyecto/requirements.txt`, con versión fija).

### Paso 2: completa el Dockerfile (10 minutos)

Edita `psets/proyecto/Dockerfile`: resuelve cada `TODO`, decidiendo el orden de las instrucciones pensando en la cache (dependencias antes que código), y agrega un volumen en tus notas si tu proyecto lee o escribe datos.

### Paso 3: construye y verifica (5 minutos)

```
docker build -t <nombre-de-tu-proyecto> .
docker run <con -v si tu proyecto usa datos> <nombre-de-tu-proyecto>
```

Confirma que el resultado dentro del contenedor coincide con correr tu código directamente en tu máquina.

Construí `docker build -t proyecto-m5 .` y corrí `docker run --rm -v "$(pwd)/data:/app/data" proyecto-m5`: la imagen carga los datos montados y el pipeline da las mismas formas que en mi máquina (entrenamiento 4 532 151 × 32, prueba 170 744 × 32). Sin diferencias.

## Antes de la próxima sesión

Ya tienes tu proyecto empaquetado en una imagen reproducible.

Pregunta: ¿qué pasa si necesitas provisionar el almacenamiento de datos donde ese contenedor va a leer y escribir, sin hacerlo a mano cada vez?

Provisionarlo con código (infraestructura como código, p. ej. Terraform): se declara el almacenamiento y se crea o recrea igual cada vez, sin pasos manuales.
