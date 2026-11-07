-- El modelo de staging es el unico que toca raw_pedidos: lista solo las
-- columnas que el resto del proyecto usa.
select
    id_pedido,
    id_cliente,
    fecha,
    categoria,
    cantidad,
    precio_unitario
from raw_pedidos
