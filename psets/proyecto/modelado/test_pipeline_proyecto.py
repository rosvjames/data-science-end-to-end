"""Pruebas de pipeline_proyecto.py. Se corren desde la raiz del repositorio con:

    pytest psets/proyecto -v

Arman sus propios datos (unas pocas filas escritas a mano): no leen
data/processed, que no existe en GitHub Actions.
"""

import numpy as np
import pandas as pd

from modelado.pipeline_proyecto import (CATEGORICAS, NUMERICAS, OBJETIVO,
                                        YA_LISTAS, LineaBaseMedia28,
                                        agregar_features,
                                        construir_preparacion,
                                        features_de_calendario)


def serie_de_un_item(dias=40, item="FOODS_1_001"):
    """Un item con units = numero del dia (1, 2, ..., dias), para poder
    calcular las features a mano."""
    return pd.DataFrame({
        "item_id": item,
        "d_num": range(1, dias + 1),
        "units": range(1, dias + 1),
        "is_pre_launch": False,
    })


def test_el_objetivo_no_es_una_columna_de_entrada():
    entradas = NUMERICAS + CATEGORICAS + YA_LISTAS
    assert OBJETIVO == "units"
    assert OBJETIVO not in entradas
    # revenue se calcula con units: usarla seria fuga de informacion.
    assert "revenue" not in entradas


def test_features_de_lag_y_media_coinciden_con_el_calculo_a_mano():
    resultado = agregar_features(serie_de_un_item()).set_index("d_num")
    # Dia 40: hace 7 dias se vendieron 33; los 28 dias previos (12 a 39) promedian 25.5.
    assert resultado.loc[40, "units_lag_7"] == 99
    assert resultado.loc[40, "units_media_28"] == 25.5
    # La primera fila con 28 dias de historia es la del dia 29 (promedio de 1 a 28).
    assert resultado.index.min() == 29
    assert resultado.loc[29, "units_media_28"] == 14.5


def test_las_features_no_miran_hacia_el_futuro():
    original = agregar_features(serie_de_un_item()).set_index("d_num")
    cambiada = serie_de_un_item()
    cambiada.loc[cambiada["d_num"] == 40, "units"] = 999  # solo cambia el ultimo dia
    cambiada = agregar_features(cambiada).set_index("d_num")
    columnas = ["units_lag_7", "units_media_28"]
    # Las features del dia 40 usan solo ventas anteriores: no cambian.
    assert (original.loc[40, columnas] == cambiada.loc[40, columnas]).all()
    # Y ningun dia anterior cambia por lo que paso despues.
    assert original.loc[:39, columnas].equals(cambiada.loc[:39, columnas])


def test_las_filas_pre_lanzamiento_se_descartan_y_no_cuentan_en_el_historial():
    datos = serie_de_un_item()
    pre = pd.DataFrame({"item_id": "FOODS_1_001", "d_num": range(-9, 1), "units": 0, "is_pre_launch": True})
    resultado = agregar_features(pd.concat([pre, datos])).set_index("d_num")
    assert resultado.index.min() == 29
    assert resultado.loc[29, "units_media_28"] == 14.5  # los ceros previos al lanzamiento no entran


def test_la_media_se_calcula_por_item_sin_mezclar_items():
    a = serie_de_un_item(item="A")
    b = serie_de_un_item(item="B")
    b["units"] = 100
    resultado = agregar_features(pd.concat([a, b]))
    medias_a = resultado.loc[resultado["item_id"] == "A", "units_media_28"]
    medias_b = resultado.loc[resultado["item_id"] == "B", "units_media_28"]
    assert (medias_b == 100).all()
    assert medias_a.max() < 40


def entrenamiento_chico():
    return pd.DataFrame({
        "sell_price": [2.0, 3.5, np.nan],
        "units_lag_7": [1, 4, 2],
        "units_media_28": [1.5, 3.0, 2.0],
        "dept_id": ["FOODS_1", "HOBBIES_1", "FOODS_1"],
        "wday": [1, 2, 3],
        "month": [1, 2, 3],
        "is_snap": [0, 1, 0],
        "is_event_day": [0, 0, 1],
        "is_weekend": [1, 0, 0],
    })


def test_la_preparacion_acepta_una_categoria_que_no_vio_al_entrenar():
    preparacion = construir_preparacion().fit(entrenamiento_chico())
    nuevo = entrenamiento_chico().iloc[:1].copy()
    nuevo["dept_id"] = "DEPARTAMENTO_NUEVO"
    columnas = preparacion.transform(nuevo)
    assert columnas.shape[0] == 1
    assert not np.isnan(columnas).any()


def test_la_preparacion_imputa_el_precio_faltante():
    preparacion = construir_preparacion().fit(entrenamiento_chico())
    columnas = preparacion.transform(entrenamiento_chico())
    assert not np.isnan(columnas).any()


def test_la_linea_base_predice_la_media_de_28_dias():
    tabla = entrenamiento_chico()
    prediccion = LineaBaseMedia28().fit(tabla).predict(tabla)
    assert list(prediccion) == [1.5, 3.0, 2.0]


def test_el_calendario_coincide_con_el_de_m5():
    # En M5, wday vale 1 el sabado y 7 el viernes; 2011-01-29 fue sabado.
    assert features_de_calendario("2011-01-29") == {"wday": 1, "month": 1, "is_weekend": 1}
    assert features_de_calendario("2011-01-31") == {"wday": 3, "month": 1, "is_weekend": 0}
    assert features_de_calendario("2011-02-04")["wday"] == 7
