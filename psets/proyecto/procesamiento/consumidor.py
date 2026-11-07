"""Consumidor del proyecto M5: cuenta las unidades vendidas por departamento
y avisa de las ventas atipicas (mas de 10 unidades de un producto en un
solo evento).

    python consumidor.py
"""

import json

from kafka import KafkaConsumer

UMBRAL_UNIDADES = 10


def deserializar_evento(datos):
    return json.loads(datos.decode("utf-8"))


consumidor = KafkaConsumer(
    "ventas_m5",
    bootstrap_servers="localhost:9092",
    value_deserializer=deserializar_evento,
    auto_offset_reset="earliest",
    consumer_timeout_ms=10000,
)

unidades_por_departamento = {}

for mensaje in consumidor:
    evento = mensaje.value
    print(f"Consumido: {evento}")
    depto = evento["dept_id"]
    unidades_por_departamento[depto] = unidades_por_departamento.get(depto, 0) + evento["units"]
    if evento["units"] > UMBRAL_UNIDADES:
        print(f"ALERTA: venta atipica de {evento['item_id']} ({evento['units']} unidades)")

print("Unidades por departamento:", unidades_por_departamento)
consumidor.close()
