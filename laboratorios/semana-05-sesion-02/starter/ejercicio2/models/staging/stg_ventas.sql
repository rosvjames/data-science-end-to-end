-- Lista las columnas que el resto del proyecto usa. id_venta 4 viene
-- repetido en raw_ventas (fila identica): distinct corrige la causa aqui,
-- sin tocar raw_ventas ni ventas.csv.
select distinct
    id_venta,
    id_producto,
    fecha,
    unidades
from raw_ventas
