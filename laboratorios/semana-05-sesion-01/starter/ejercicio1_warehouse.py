"""Ejercicio 1: un warehouse local con pedidos.csv y clientes.csv.

Corre el script antes de tocar nada:

    python3 ejercicio1_warehouse.py

Corre sin errores y sin los TODO resueltos: mientras no exista la tabla,
las consultas leen el CSV directamente.
"""

import duckdb

con = duckdb.connect("almacen.duckdb")

print("Paso 1: cargar pedidos.csv al warehouse")
# TODO 1: crea la tabla pedidos con el contenido de pedidos.csv, y despues
# cambia ORIGEN_PEDIDOS por el nombre de la tabla.
con.execute("CREATE OR REPLACE TABLE pedidos AS SELECT * FROM read_csv_auto('pedidos.csv')")
ORIGEN_PEDIDOS = "pedidos"
print("Tablas en el warehouse:")
print(con.execute("SHOW TABLES").df())

print()
print("Paso 2: cuantas filas hay")
# TODO 2: cuenta las filas de ORIGEN_PEDIDOS con una consulta SQL.
total_filas = con.execute(f"SELECT COUNT(*) FROM {ORIGEN_PEDIDOS}").fetchone()[0]
print(f"Filas de pedidos: {total_filas}")

print()
print("Paso 3: monto por categoria")
# TODO 3: agrega por categoria: numero de pedidos y monto total
# (cantidad * precio_unitario), del monto mas alto al mas bajo.
por_categoria = con.execute(f"""
    SELECT categoria, COUNT(*) AS pedidos, SUM(cantidad * precio_unitario) AS monto
    FROM {ORIGEN_PEDIDOS}
    GROUP BY categoria
    ORDER BY monto DESC
""").df()
print(por_categoria)

print()
print("Paso 4: monto por ciudad")
# TODO 4: carga clientes.csv como tabla clientes y une las dos tablas por
# id_cliente para obtener el monto total por ciudad.
con.execute("CREATE OR REPLACE TABLE clientes AS SELECT * FROM read_csv_auto('clientes.csv')")
por_ciudad = con.execute("""
    SELECT c.ciudad, SUM(p.cantidad * p.precio_unitario) AS monto
    FROM pedidos p
    JOIN clientes c ON p.id_cliente = c.id_cliente
    GROUP BY c.ciudad
    ORDER BY monto DESC
""").df()
print(por_ciudad)

con.close()
