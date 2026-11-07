-- Une pedidos y clientes leyendo los modelos de staging con ref(): dbt
-- construye primero staging y despues este modelo.
select
    p.id_pedido,
    p.fecha,
    p.categoria,
    p.cantidad * p.precio_unitario as monto_total,
    c.ciudad,
    c.segmento
from {{ ref('stg_pedidos') }} as p
join {{ ref('stg_clientes') }} as c on p.id_cliente = c.id_cliente
