"""Preparacion de los datos de mi proyecto, lista para produccion.

Proyecto M5 (ventas de Walmart, tienda CA_1): predecir las unidades vendidas
de un item en la tienda al dia siguiente (grain: item x tienda x dia).

Momento de la prediccion: al cierre del dia anterior. Existen las ventas
hasta ayer, el precio vigente, el calendario (dia de la semana, eventos,
SNAP) del dia a predecir. No existe el revenue de hoy, porque se calcula con
el objetivo (fuga de informacion).

Los notebooks de experimentos importan este archivo:

    from pipeline_proyecto import cargar_y_dividir, construir_preparacion

Para comprobar que corre de principio a fin, sin notebook:

    python3 pipeline_proyecto.py
"""

import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RUTA_DATOS = "../data/processed/obt_sales_CA_1.csv.gz"

OBJETIVO = "units"
NUMERICAS = ["sell_price", "units_lag_7", "units_media_28"]
CATEGORICAS = ["dept_id", "wday", "month"]
YA_LISTAS = ["is_snap", "is_event_day", "is_weekend"]

COLUMNAS_LEIDAS = [
    "d_num", "item_id", "dept_id", "units", "sell_price", "wday", "month",
    "is_snap", "is_event_day", "is_weekend", "is_pre_launch",
]

# Dias al final de la serie que quedan como prueba (8 semanas): se predice el
# futuro, asi que la division es por fecha, no al azar.
DIAS_DE_PRUEBA = 56


def agregar_features(datos):
    """Las 2 features nuevas, calculadas solo con ventas de dias anteriores.

    units_lag_7: unidades del mismo item hace 7 dias (mismo dia de la
        semana de la semana pasada).
    units_media_28: promedio de unidades del item en los 28 dias anteriores,
        sin incluir el dia a predecir.
    Se calculan por item, despues de quitar las filas pre-lanzamiento (ceros
    sin precio que no son demanda real).
    """
    datos = datos.query("not is_pre_launch").sort_values(["item_id", "d_num"]).copy()
    por_item = datos.groupby("item_id", sort=False)["units"]
    datos["units_lag_7"] = por_item.shift(7)
    datos["units_media_28"] = por_item.transform(lambda s: s.shift(1).rolling(28).mean())
    return datos.dropna(subset=["units_lag_7", "units_media_28"])


def features_de_calendario(fecha):
    """Las columnas de calendario de un dia, calculadas igual que en la OBT:
    wday va de 1 (sabado) a 7 (viernes), como en M5."""
    fecha = pd.Timestamp(fecha)
    return {
        "wday": (fecha.dayofweek + 2) % 7 + 1,
        "month": fecha.month,
        "is_weekend": int(fecha.dayofweek >= 5),
    }


def cargar_completo(ruta=RUTA_DATOS):
    """Todas las filas con sus features y la columna d_num (el dia), sin
    dividir. Sirve para validacion cruzada."""
    datos = agregar_features(pd.read_csv(ruta, usecols=COLUMNAS_LEIDAS))
    for columna in YA_LISTAS:
        datos[columna] = datos[columna].astype(int)
    return datos


def cargar_y_dividir(ruta=RUTA_DATOS, maximo_entrenamiento=None):
    """Devuelve X_ent, X_prueba, y_ent, y_prueba, divididos por fecha.

    maximo_entrenamiento: si se da, usa solo esa cantidad de filas de
    entrenamiento (muestra al azar con random_state=42) para entrenar rapido.
    La prueba siempre queda completa.
    """
    datos = cargar_completo(ruta)
    corte = datos["d_num"].max() - DIAS_DE_PRUEBA
    ent = datos[datos["d_num"] <= corte]
    prueba = datos[datos["d_num"] > corte]
    if maximo_entrenamiento is not None and len(ent) > maximo_entrenamiento:
        ent = ent.sample(maximo_entrenamiento, random_state=42)
    columnas = NUMERICAS + CATEGORICAS + YA_LISTAS
    return ent[columnas], prueba[columnas], ent[OBJETIVO], prueba[OBJETIVO]


class LineaBaseMedia28(BaseEstimator, RegressorMixin):
    """Linea base del proyecto: la demanda de manana es el promedio de los
    28 dias previos del item. No aprende nada; recibe la tabla sin preparar."""

    def fit(self, X, y=None):
        return self

    def predict(self, X):
        return X["units_media_28"].to_numpy()


def construir_preparacion():
    return ColumnTransformer([
        ("numericas", Pipeline([
            ("imputar", SimpleImputer(strategy="median")),
            ("escalar", StandardScaler()),
        ]), NUMERICAS),
        ("categoricas", Pipeline([
            ("imputar", SimpleImputer(strategy="most_frequent")),
            ("codificar", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), CATEGORICAS),
        ("ya_listas", "passthrough", YA_LISTAS),
    ])


# Esto corre con "python3 pipeline_proyecto.py", pero no cuando un
# notebook hace "from pipeline_proyecto import ...".
if __name__ == "__main__":
    X_ent, X_prueba, y_ent, y_prueba = cargar_y_dividir()
    preparacion = construir_preparacion()
    X_ent_listo = preparacion.fit_transform(X_ent)
    X_prueba_listo = preparacion.transform(X_prueba)
    print("Entrenamiento:", X_ent_listo.shape, "Prueba:", X_prueba_listo.shape)
    print(list(preparacion.get_feature_names_out()))
