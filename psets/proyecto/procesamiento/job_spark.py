"""Job de Spark del proyecto M5 (tienda CA_1): la misma agregacion por
departamento del warehouse (unidades y proporcion de ceros), sobre el
historico completo. Se corre desde esta carpeta:

    python job_spark.py
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("m5-ca1-por-departamento").master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

historico = spark.read.csv("../data/processed/obt_sales_CA_1.csv.gz", header=True, inferSchema=True)
print(f"Particiones de lectura: {historico.rdd.getNumPartitions()}")
print(f"Filas leidas: {historico.count()}")

resultado = (
    historico
    .filter(~F.col("is_pre_launch"))
    .withColumn("es_cero", (F.col("units") == 0).cast("int"))
    .groupBy("dept_id")
    .agg(
        F.sum("units").alias("unidades"),
        F.round(F.avg("units"), 3).alias("unidades_por_dia"),
        F.round(F.avg("es_cero"), 3).alias("proporcion_ceros"),
    )
    .orderBy(F.desc("unidades"))
)
resultado.show()

resultado.write.mode("overwrite").csv("resultado_por_departamento", header=True)

spark.stop()
