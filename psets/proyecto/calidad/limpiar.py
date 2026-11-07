"""Etapa de calidad del pipeline M5 (tienda CA_1): aplica las decisiones del
diagnostico (diagnostico_proyecto.ipynb) y falla si algo no se cumple.

    python limpiar.py

Decisiones: sin duplicados (0 encontrados: se verifica), fechas con formato
AAAA-MM-DD (se verifica), sin unidades negativas ni precios <= 0, y los
faltantes de precio solo pueden ser dias pre-lanzamiento. Las filas
pre-lanzamiento se conservan en el archivo (el warehouse y el pipeline las
filtran) y revenue no se usa como variable de entrada. El archivo ya esta
limpio: esta etapa no crea una copia, deja un reporte.
"""

import pandas as pd

RUTA = "../data/processed/obt_sales_CA_1.csv.gz"

datos = pd.read_csv(RUTA)

duplicados = int(datos.duplicated(["item_id", "date"]).sum())
fechas_mal = int(pd.to_datetime(datos["date"], format="%Y-%m-%d", errors="coerce").isna().sum())
negativas = int((datos["units"] < 0).sum())
precios_invalidos = int((datos["sell_price"] <= 0).sum())
precio_faltante_fuera_de_prelanzamiento = int((datos["sell_price"].isna() & ~datos["is_pre_launch"]).sum())

reporte = pd.Series({
    "filas": len(datos),
    "duplicados": duplicados,
    "fechas_con_formato_incorrecto": fechas_mal,
    "unidades_negativas": negativas,
    "precios_menores_o_iguales_a_0": precios_invalidos,
    "precio_faltante_fuera_de_prelanzamiento": precio_faltante_fuera_de_prelanzamiento,
    "filas_prelanzamiento": int(datos["is_pre_launch"].sum()),
})
print(reporte.to_string())
reporte.to_csv("reporte_calidad.csv", header=["valor"])

problemas = reporte.drop(["filas", "filas_prelanzamiento"])
assert (problemas == 0).all(), f"El archivo no cumple las reglas de calidad:\n{problemas[problemas > 0]}"
print("OK: el archivo cumple las reglas de calidad")
