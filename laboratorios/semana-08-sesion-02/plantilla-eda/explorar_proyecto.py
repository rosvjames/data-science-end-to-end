import os

import matplotlib.pyplot as plt
import pandas as pd

os.makedirs("figuras", exist_ok=True)

# OBT.OBT_SALES del pipeline M5 (pset2), exportada de Snowflake y filtrada
# a la tienda CA_1 (5.9 M de las 59 M filas). Grain: item x tienda x dia.
datos = pd.read_csv("obt_sales_CA_1.csv.gz")

# Unidades vendidas del item en la tienda ese dia.
OBJETIVO = "units"

# Paso 1: resumen.
print("Filas y columnas:", datos.shape)
print(datos.dtypes)
print(datos.isna().sum())
print(datos.describe().round(2))

# Paso 2: distribucion de la variable objetivo.
plt.figure()
plt.hist(datos[OBJETIVO], bins=40)
plt.title(OBJETIVO)
plt.savefig("figuras/distribucion_objetivo.png")
plt.close()

# Paso 3: atipicos de la variable objetivo con la regla del IQR.
q1 = datos[OBJETIVO].quantile(0.25)
q3 = datos[OBJETIVO].quantile(0.75)
iqr = q3 - q1
fuera = datos[(datos[OBJETIVO] < q1 - 1.5 * iqr) | (datos[OBJETIVO] > q3 + 1.5 * iqr)]
print(f"Atipicos de {OBJETIVO} segun IQR: {len(fuera)}")
print(fuera.head(10))

# Paso 4: promedio de unidades por departamento (variable categorica).
por_depto = datos.groupby("dept_id")[OBJETIVO].mean().sort_values()
print(por_depto.round(2))
plt.figure(figsize=(8, 5))
por_depto.plot.barh()
plt.title(f"{OBJETIVO} promedio por departamento")
plt.xlabel(f"{OBJETIVO} promedio")
plt.tight_layout()
plt.savefig("figuras/objetivo_por_departamento.png")
plt.close()

# Paso 5: consultas que confirman los hallazgos.

# Hallazgo 1: filas antes del lanzamiento del item (units 0 y sin precio).
pre = datos.query("is_pre_launch")
print(f"Filas pre-lanzamiento: {len(pre)} ({len(pre) / len(datos):.1%})")
print(pre[[OBJETIVO, "sell_price"]].describe().round(2))
print(f"Ceros de {OBJETIVO}: {(datos[OBJETIVO] == 0).mean():.1%} del total, "
      f"{(datos.query('not is_pre_launch')[OBJETIVO] == 0).mean():.1%} sin pre-lanzamiento")

# Hallazgo 2: ceros que no son falta de demanda (quiebre de stock, tienda cerrada).
vendibles = datos.query("not is_pre_launch")
ceros = vendibles.query(f"{OBJETIVO} == 0")
print(f"Ceros marcados como quiebre (conservador): {ceros['is_suspected_stockout_conservative'].mean():.1%}")
print(f"Ceros marcados como quiebre (binomial negativa): {ceros['is_suspected_stockout_nb'].mean():.1%}")
print(vendibles.groupby("is_christmas_closed")[OBJETIVO].agg(["size", "mean"]).round(2))

# Hallazgo 3: revenue se calcula con el objetivo (fuga de informacion).
con_precio = vendibles.dropna(subset=["sell_price"])
print(f"revenue == units * sell_price: "
      f"{((con_precio['revenue'] - con_precio[OBJETIVO] * con_precio['sell_price']).abs() < 0.01).mean():.1%}")
print(vendibles[[OBJETIVO, "revenue", "sell_price", "is_snap", "is_event_day", "is_weekend"]]
      .corr()[OBJETIVO].round(3))
