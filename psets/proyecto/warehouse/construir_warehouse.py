"""Warehouse local del proyecto M5 (tienda CA_1): carga la OBT en DuckDB y
hace las primeras consultas. Se corre desde esta carpeta:

    python construir_warehouse.py
"""

import duckdb

con = duckdb.connect("m5.duckdb")

con.execute("""
    CREATE OR REPLACE TABLE ventas_ca1 AS
    SELECT * FROM read_csv_auto('../data/processed/obt_sales_CA_1.csv.gz')
""")

total_filas = con.execute("SELECT COUNT(*) FROM ventas_ca1").fetchone()[0]
print(f"Filas cargadas: {total_filas}")

# Pregunta: que departamentos venden mas, y que proporcion de sus dias son
# ceros reales (producto ya lanzado y sin ventas)?
resultado = con.execute("""
    SELECT dept_id,
           SUM(units) AS unidades,
           ROUND(AVG(units), 3) AS unidades_por_dia,
           ROUND(AVG((units = 0)::INT), 3) AS proporcion_ceros
    FROM ventas_ca1
    WHERE NOT is_pre_launch
    GROUP BY dept_id
    ORDER BY unidades DESC
""").df()
print(resultado)

con.close()
