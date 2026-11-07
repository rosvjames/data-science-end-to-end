"""Ejercicio 1, consumidor: lee los pedidos del topico pedidos.

Corre el productor primero y despues:

    python3 ejercicio1_consumidor.py

Espera 10 segundos sin eventos nuevos y termina.
"""

import json

from kafka import KafkaConsumer


def deserializar_evento(datos):
    # TODO 3: deshace lo que hizo serializar_evento en el productor.
    return json.loads(datos.decode("utf-8"))


consumidor = KafkaConsumer(
    "pedidos",
    bootstrap_servers="localhost:9092",
    value_deserializer=deserializar_evento,
    # TODO 2: lee el topico desde el primer evento, no solo los que
    # lleguen despues de arrancar.
    auto_offset_reset="earliest",
    consumer_timeout_ms=10000,
)

conteo_por_categoria = {}

for mensaje in consumidor:
    evento = mensaje.value
    print(f"Consumido: {evento}")
    # TODO 4: suma 1 al conteo de la categoria de este evento.
    conteo_por_categoria[evento["categoria"]] = conteo_por_categoria.get(evento["categoria"], 0) + 1

print("Resumen final:", conteo_por_categoria)
consumidor.close()
