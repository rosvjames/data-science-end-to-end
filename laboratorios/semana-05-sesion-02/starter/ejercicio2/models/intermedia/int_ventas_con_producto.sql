-- Une las ventas con su producto y calcula el monto de cada venta.
select
    v.id_venta,
    v.fecha,
    v.id_producto,
    p.categoria,
    v.unidades,
    v.unidades * p.precio as monto
from {{ ref('stg_ventas') }} as v
join {{ ref('stg_productos') }} as p on v.id_producto = p.id_producto
