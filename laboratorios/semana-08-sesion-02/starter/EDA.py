import pandas as pd
import os
import matplotlib.pyplot as plt

os.makedirs('./starter/figuras', exist_ok=True)

data = pd.read_csv('./starter/viajes_taxi.csv')

print('Analisis exploratorio descriptivo')

data.info()

print(data.dtypes)
print(data.isna().sum())
print(data.duplicated().sum())

print(data.describe())

plt.figure(figsize=(10, 6))
plt.hist(data['tarifa'], bins=50)
plt.title('Distribución de la tarifa')
plt.xlabel('USD')
plt.ylabel('Numero de viajes')
plt.savefig('./starter/figuras/hist_tarifa.png')
plt.close()

plt.figure(figsize=(10, 6))
plt.boxplot(data['tarifa'])
plt.title('Boxplot de la tarifa')
plt.savefig('./starter/figuras/boxplot_tarifa.png')
plt.close()

# Extraccion de valores atipicos

q1 = data['tarifa'].quantile(0.25)
q3 = data['tarifa'].quantile(0.75)
iqr = q3 - q1

limite_superior = q3 + 1.5 * iqr
limite_inferior = q1 - 1.5 * iqr

atipicos = data.query(f'tarifa < {limite_inferior} or tarifa > {limite_superior}')
print(f'Atipicos por IQR: {len(atipicos)}')

# Investigacion de los atipicos: no todos son errores

print(atipicos['tarifa'].value_counts().head(10))
print(atipicos['zona_origen'].value_counts())
print(atipicos['zona_destino'].value_counts())

errores = atipicos.query('tarifa == 999.99')
atipicos_reales = atipicos.query('tarifa != 999.99')
viajes_jfk = atipicos_reales.query("zona_origen == 'JFK Airport' or zona_destino == 'JFK Airport'")

print(f'Errores de captura (tarifa 999.99): {len(errores)}')
print(f'Atipicos legitimos: {len(atipicos_reales)}')
print(f'  de ellos, viajes desde o hacia JFK: {len(viajes_jfk)}')
print(atipicos_reales['tarifa'].describe())

# Otros valores imposibles que muestra describe()

print(f'Duracion negativa: {(data["duracion_min"] < 0).sum()}')
print(f'Distancia 0: {(data["distancia_km"] == 0).sum()}')

# Solo se quitan los errores confirmados; los viajes a JFK se conservan

limpio = data.query('tarifa != 999.99')
print(f'Filas tras quitar errores: {len(limpio)}')

plt.figure()
plt.scatter(data['distancia_km'], data['tarifa'])
plt.title('Dispersión de distancia_km vs tarifa')
plt.xlabel('distancia_km')
plt.ylabel('tarifa (USD)')
plt.savefig('./starter/figuras/dispersion_distancia_km_vs_tarifa.png')
plt.close()

plt.figure()
plt.scatter(limpio['distancia_km'], limpio['tarifa'])
plt.title('Dispersión de distancia_km vs tarifa (sin errores)')
plt.xlabel('distancia_km')
plt.ylabel('tarifa (USD)')
plt.savefig('./starter/figuras/dispersion_distancia_km_vs_tarifa_sin_errores.png')
plt.close()
