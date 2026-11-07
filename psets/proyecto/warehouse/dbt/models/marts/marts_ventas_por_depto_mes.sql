-- Pregunta: cuantas unidades vende cada departamento por mes, y que
-- proporcion de sus dias son ceros.
select
    dept_id,
    mes,
    sum(units) as unidades,
    avg((units = 0)::int) as proporcion_ceros
from {{ ref('int_ventas_vendibles') }}
group by dept_id, mes
order by dept_id, mes
