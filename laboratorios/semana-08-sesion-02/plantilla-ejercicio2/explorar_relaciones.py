import os

import matplotlib.pyplot as plt
import pandas as pd

os.makedirs("figuras", exist_ok=True)
viajes = pd.read_csv("../starter/viajes_taxi.csv")

# TODO 1: quita solo los errores que el Ejercicio 1 ya confirmo (tarifa
# 999.99 y duracion negativa). No quites los demas atipicos. Imprime
# cuantas filas quedan.
limpios = viajes.query("tarifa != 999.99 and duracion_min >= 0")
print(f"Filas tras quitar errores: {len(limpios)}")

# TODO 2: grafico de dispersion de distancia_km (eje x) contra tarifa
# (eje y), guardado en figuras/distancia_vs_tarifa.png. Mira el grafico
# antes de seguir: busca puntos que no sigan la tendencia general y
# cuentalos con un filtro.
plt.figure()
plt.scatter(limpios["distancia_km"], limpios["tarifa"], s=8, alpha=0.5)
plt.title("Distancia vs tarifa")
plt.xlabel("distancia_km")
plt.ylabel("tarifa (USD)")
plt.savefig("figuras/distancia_vs_tarifa.png")
plt.close()

tarifa_fija = limpios.query("tarifa == 70")
print(f"Viajes con tarifa fija de 70: {len(tarifa_fija)}")
print(tarifa_fija[["zona_origen", "zona_destino"]].value_counts())
distancia_cero = limpios.query("distancia_km == 0")
print(f"Viajes con distancia 0: {len(distancia_cero)}")
print(distancia_cero["tarifa"].describe())

# TODO 3: propina promedio y cantidad de viajes con propina 0, por
# metodo de pago (groupby + agg).
propinas = limpios.groupby("metodo_pago", dropna=False).agg(
    viajes=("propina", "size"),
    propina_promedio=("propina", "mean"),
    propina_cero=("propina", lambda p: (p == 0).sum()),
)
print(propinas)

# TODO 4: correlacion de distancia_km, duracion_min, pasajeros y propina
# con la tarifa.
columnas = ["distancia_km", "duracion_min", "pasajeros", "propina", "tarifa"]
print(limpios[columnas].corr()["tarifa"].drop("tarifa"))

# TODO 5: cuantos viajes tienen pasajeros vacio y cuantos tienen 0.
print(f"Pasajeros vacio: {limpios['pasajeros'].isna().sum()}")
print(f"Pasajeros en 0: {(limpios['pasajeros'] == 0).sum()}")
