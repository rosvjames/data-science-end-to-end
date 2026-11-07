"""Servicio de prediccion de la demanda: unidades de un producto en CA_1 al
dia siguiente.

Quien llama manda lo que conoce al cierre del dia anterior: el producto
(departamento), la fecha a predecir, el precio vigente, si es dia SNAP o de
evento, y las ventas diarias recientes del producto (al menos 28 dias, del
mas antiguo al mas reciente, hasta ayer). El servicio calcula el resto de las
features con las mismas funciones de modelado/pipeline_proyecto.py.

Desde psets/proyecto/, despues de exportar el modelo:

    uvicorn servicio.api:app --port 8000
"""

import hashlib
import os
from datetime import date

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from modelado.pipeline_proyecto import (CATEGORICAS, NUMERICAS, YA_LISTAS,
                                        agregar_features, features_de_calendario)

RUTA_MODELO = os.environ.get("RUTA_MODELO", os.path.join(os.path.dirname(__file__), "modelo.joblib"))
DIAS_MINIMOS = 28

modelo = None
version_modelo = None
if os.path.exists(RUTA_MODELO):
    modelo = joblib.load(RUTA_MODELO)
    with open(RUTA_MODELO, "rb") as archivo:
        version_modelo = hashlib.md5(archivo.read()).hexdigest()[:12]

app = FastAPI(title="Demanda de productos (M5, CA_1)")


class Consulta(BaseModel):
    """Lo que sabe quien llama al cierre del dia anterior."""
    fecha: date
    dept_id: str
    sell_price: float | None = None
    is_snap: bool = False
    is_event_day: bool = False
    ventas_recientes: list[float] = Field(min_length=DIAS_MINIMOS)


def construir_fila(consulta):
    """Arma la fila de entrada del modelo reutilizando agregar_features: el
    historial y el dia a predecir (con units vacio) van en una sola serie."""
    n = len(consulta.ventas_recientes)
    serie = pd.DataFrame({
        "item_id": "consulta",
        "d_num": range(n + 1),
        "units": [*consulta.ventas_recientes, np.nan],
        "is_pre_launch": False,
    })
    fila = agregar_features(serie).iloc[[-1]].copy()
    fila["sell_price"] = consulta.sell_price if consulta.sell_price is not None else np.nan
    fila["dept_id"] = consulta.dept_id
    fila["is_snap"] = int(consulta.is_snap)
    fila["is_event_day"] = int(consulta.is_event_day)
    for columna, valor in features_de_calendario(consulta.fecha).items():
        fila[columna] = valor
    return fila[NUMERICAS + CATEGORICAS + YA_LISTAS]


@app.get("/salud")
def salud():
    return {"estado": "ok", "modelo_cargado": modelo is not None, "version_modelo": version_modelo}


@app.post("/predecir")
def predecir(consulta: Consulta):
    if modelo is None:
        raise HTTPException(status_code=503, detail="El servicio no tiene modelo cargado")
    unidades = float(modelo.predict(construir_fila(consulta))[0])
    return {"unidades_estimadas": round(max(unidades, 0.0), 2), "version_modelo": version_modelo}
