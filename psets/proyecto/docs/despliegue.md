# Despliegue del modelo: por lotes

**Decisión: el modelo se sirve por lotes, una vez por noche.**

## Qué decisión habilita y cuánto puede esperar

La predicción son las unidades que se venderán de cada producto, en la tienda CA_1, al día siguiente. La usa el encargado de reposición para decidir cuánto pedir y cuánto reponer en góndola antes de abrir. Puede esperar horas: el pedido se arma una vez al día, así que lo que se necesita es tener las predicciones listas antes de ese pedido (por ejemplo, a las 5:00 de la mañana). El límite de latencia es de unas horas, no de milisegundos.

## Cuántos casos hay y si se conocen de antemano

Unos 3 049 productos en una tienda, un día a la vez. Los casos se conocen de antemano: el catálogo de la tienda es una lista fija, y para cada producto basta una predicción por día. Se pueden calcular todos de una vez, en una pasada.

## Qué datos necesitan las features al predecir

Se necesita el historial de ventas del producto hasta el día anterior (`units_lag_7`, `units_media_28`), el precio vigente (`sell_price`) y el calendario del día a predecir (día de la semana, mes, eventos, SNAP). Todo existe al cierre del día anterior, que es cuando corre el lote. Las features de historial son justamente las que obligan a esperar al cierre: durante el día todavía no existe la venta completa de hoy.

## Qué se pierde con el patrón que descarto (online)

Un servicio en línea permitiría predecir con ventas del mismo día (por ejemplo, reaccionar a un producto que se agota a las 11:00) y atender productos nuevos sin esperar a la noche. Pero la decisión de reposición no se toma varias veces al día, así que ese beneficio no se aprovecha, mientras que sí tendría un costo fijo: mantener un servicio disponible las 24 horas, con monitoreo y manejo de fallas. Lo que se pierde con batch es la reacción intradía y los productos que nacen durante el día, que se cubren con la predicción de la noche siguiente. Aun así, el proyecto también construye un servicio de predicción (Semana 12, sesión 2) para que otros sistemas puedan pedirle una predicción puntual.
