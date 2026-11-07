-- Unico modelo que toca ventas_ca1: columnas que usa el resto del proyecto,
-- mas una clave por producto y dia (la tabla no tiene una sola columna unica).
select
    item_id || '-' || cast(date as varchar) as clave_item_dia,
    item_id,
    dept_id,
    cast(date as date) as fecha,
    units,
    sell_price,
    is_pre_launch
from ventas_ca1
