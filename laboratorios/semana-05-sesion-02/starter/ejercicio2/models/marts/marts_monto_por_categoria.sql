-- Monto total por categoria.
select
    categoria,
    sum(monto) as monto_total
from {{ ref('int_ventas_con_producto') }}
group by categoria
order by monto_total desc
