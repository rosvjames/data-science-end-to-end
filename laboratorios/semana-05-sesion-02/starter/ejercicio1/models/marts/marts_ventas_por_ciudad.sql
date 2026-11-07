-- Cuanto se vendio por ciudad: numero de pedidos y monto total.
select
    ciudad,
    count(*) as pedidos,
    sum(monto_total) as monto_total
from {{ ref('int_pedidos_con_cliente') }}
group by ciudad
order by monto_total desc
