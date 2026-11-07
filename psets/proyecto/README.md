# [Nombre de tu proyecto]

> Este es el README de tu proyecto: reemplaza cada sección entre corchetes a medida que avanzas. Escríbelo para alguien que clona tu fork sin haber estado en clase y necesita entender qué hace el proyecto y correrlo, no como una nota para ti.

[Un párrafo: qué problema de negocio resuelve, para quién, y qué predice el modelo. Sale de tu propuesta del PSet 1, que está completa en `docs/`.]

**Métrica de éxito:** [la métrica de negocio y el umbral de decisión del PSet 1]

## Datos

| Fuente | Qué contiene | Cómo se obtiene | Dónde queda |
|---|---|---|---|
| [nombre de la fuente] | [qué filas y columnas trae, desde qué fecha] | [la URL, la API o el procedimiento exacto] | `data/raw/[archivo]` |

Los datos no están en el repositorio. Para regenerarlos desde cero: [los comandos, en orden]. Se completa con el PSet 1.

## Cómo correr el pipeline de datos

[Los comandos, en orden y desde qué carpeta, para ir de la fuente al warehouse: levantar la infraestructura, construir la imagen, subir el flow a Kestra, limpiar, cargar y correr dbt. Cada paso dice qué archivo deja y dónde. Se completa con el PSet 2.]

## Cómo entrenar y evaluar el modelo

[Qué notebook corre cada etapa del modelado, en qué orden, y qué necesita levantado (MLflow). Se completa con el PSet 3.]

## Modelo final

[El modelo elegido, su `run_id` en MLflow y la métrica que lo sostiene. El razonamiento completo está en `docs/decision_modelo.md`. Se completa con el PSet 3.]

## Cómo correr el servicio

El servicio expone el modelo final (gradient boosting, corrida con la etiqueta `candidato = final` en el experimento `m5-demanda-CA_1` de MLflow) con dos rutas: `GET /salud` y `POST /predecir`. Todo se corre desde `psets/proyecto/`.

1. Exportar el modelo desde MLflow (el servidor tiene que estar levantado y `MLFLOW_TRACKING_URI` definida). Esto crea `servicio/modelo.joblib`, que no se sube al repositorio:

   ```bash
   python servicio/exportar_modelo.py
   ```

2. Construir la imagen y levantar el contenedor (el contexto es `psets/proyecto/`, porque la imagen necesita `modelado/` además de `servicio/`):

   ```bash
   docker build -f servicio/Dockerfile -t servicio-demanda .
   docker run -p 8000:8000 servicio-demanda
   ```

   Sin contenedor: `uvicorn servicio.api:app --port 8000`. La documentación interactiva queda en `/docs`.

3. Pedir una predicción. Se manda el departamento, la fecha a predecir, el precio, si es día SNAP o de evento, y las ventas diarias recientes del producto (al menos 28 días, del más antiguo al más reciente, hasta el día anterior). El servicio calcula `units_lag_7`, `units_media_28` y el calendario con las funciones de `modelado/pipeline_proyecto.py`:

   ```bash
   curl -X POST localhost:8000/predecir -H "Content-Type: application/json" \
     -d '{"fecha": "2016-05-22", "dept_id": "FOODS_1", "sell_price": 2.24, "is_snap": false, "is_event_day": false, "ventas_recientes": [1, 1, 0, 2, 0, 0, 0, 0, 1, 1, 0, 6, 1, 0, 3, 0, 0, 0, 2, 0, 0, 2, 3, 1, 0, 0, 0, 1, 0, 0]}'
   ```

   Respuesta: `{"unidades_estimadas": 0.99, "version_modelo": "2775572759c4"}`. Un historial de menos de 28 días recibe un error 422.

Las pruebas del servicio (`servicio/test_api.py`) no necesitan el modelo exportado: `pytest psets/proyecto -v`.
