"""Productor del proyecto M5: publica ventas de productos de CA_1 como
eventos, uno por venta registrada en caja. Con Redpanda levantado
(docker compose up -d en laboratorios/semana-06-sesion-02/starter):

    python productor.py
"""

import json
import time

from kafka import KafkaProducer


def serializar_evento(evento):
    return json.dumps(evento).encode("utf-8")


productor = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=serializar_evento,
)

topico = "ventas_m5"

eventos_a_publicar = [
    {"fecha": "2016-05-23", "item_id": "FOODS_3_090", "dept_id": "FOODS_3", "units": 4, "sell_price": 1.25, "is_snap": 0},
    {"fecha": "2016-05-23", "item_id": "FOODS_3_586", "dept_id": "FOODS_3", "units": 2, "sell_price": 1.98, "is_snap": 0},
    {"fecha": "2016-05-23", "item_id": "HOUSEHOLD_1_118", "dept_id": "HOUSEHOLD_1", "units": 1, "sell_price": 5.47, "is_snap": 0},
    {"fecha": "2016-05-23", "item_id": "HOBBIES_1_004", "dept_id": "HOBBIES_1", "units": 3, "sell_price": 3.97, "is_snap": 0},
    {"fecha": "2016-05-23", "item_id": "FOODS_3_090", "dept_id": "FOODS_3", "units": 15, "sell_price": 1.25, "is_snap": 0},
    {"fecha": "2016-05-23", "item_id": "FOODS_2_171", "dept_id": "FOODS_2", "units": 2, "sell_price": 2.98, "is_snap": 0},
]

for evento in eventos_a_publicar:
    productor.send(topico, value=evento)
    print(f"Publicado: {evento}")
    time.sleep(0.5)

productor.flush()
productor.close()
print("Productor terminado")
