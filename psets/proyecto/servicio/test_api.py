"""Pruebas del servicio. Se corren desde la raiz del repositorio con:

    pytest psets/proyecto -v

Reemplazan el modelo guardado por uno de prueba: no necesitan modelo.joblib,
que no existe en GitHub Actions.
"""

import pandas as pd
from fastapi.testclient import TestClient
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import Pipeline

from modelado.pipeline_proyecto import (CATEGORICAS, NUMERICAS, YA_LISTAS,
                                        construir_preparacion)
from servicio import api

CONSULTA = {
    "fecha": "2011-01-31",  # lunes
    "dept_id": "FOODS_1",
    "sell_price": 2.5,
    "is_snap": True,
    "is_event_day": False,
    "ventas_recientes": list(range(1, 41)),  # 1, 2, ..., 40
}


def modelo_de_prueba():
    entrenamiento = pd.DataFrame({
        "sell_price": [2.0, 3.0], "units_lag_7": [1.0, 2.0], "units_media_28": [1.0, 2.0],
        "dept_id": ["FOODS_1", "HOBBIES_1"], "wday": [1, 2], "month": [1, 2],
        "is_snap": [0, 1], "is_event_day": [0, 0], "is_weekend": [1, 0],
    })
    modelo = Pipeline([("preparar", construir_preparacion()), ("modelo", DummyRegressor(strategy="constant", constant=2.0))])
    return modelo.fit(entrenamiento[NUMERICAS + CATEGORICAS + YA_LISTAS], [2.0, 2.0])


api.modelo = modelo_de_prueba()
api.version_modelo = "abc123"
cliente = TestClient(api.app)


def test_salud():
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok", "modelo_cargado": True, "version_modelo": "abc123"}


def test_prediccion_valida():
    respuesta = cliente.post("/predecir", json=CONSULTA)
    assert respuesta.status_code == 200
    assert respuesta.json() == {"unidades_estimadas": 2.0, "version_modelo": "abc123"}


def test_el_servicio_calcula_las_features_como_el_pipeline():
    fila = api.construir_fila(api.Consulta(**CONSULTA))
    # Ventas 1..40: hace 7 dias se vendieron 34, y el promedio de los ultimos 28 dias (13 a 40) es 26.5.
    assert fila.loc[fila.index[0], "units_lag_7"] == 34
    assert fila.loc[fila.index[0], "units_media_28"] == 26.5
    # 2011-01-31 fue lunes: wday 3 en M5 (1 es sabado), entre semana, mes 1.
    assert (fila.iloc[0][["wday", "month", "is_weekend", "is_snap"]] == [3, 1, 0, 1]).all()


def test_historial_corto_se_rechaza():
    consulta = {**CONSULTA, "ventas_recientes": [1.0] * 10}
    respuesta = cliente.post("/predecir", json=consulta)
    assert respuesta.status_code == 422


def test_fecha_faltante_se_rechaza():
    consulta = {clave: valor for clave, valor in CONSULTA.items() if clave != "fecha"}
    assert cliente.post("/predecir", json=consulta).status_code == 422
