-- Solo las filas en que el producto ya estaba a la venta (sin los dias
-- pre-lanzamiento, que son ceros sin precio) y con el mes de cada fila.
select
    item_id,
    dept_id,
    fecha,
    date_trunc('month', fecha) as mes,
    units,
    units * sell_price as ingreso
from {{ ref('stg_ventas_ca1') }}
where not is_pre_launch
