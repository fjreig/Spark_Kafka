from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StructField,FloatType,IntegerType, StringType
from pyspark.sql.functions import from_json,col

import pyspark
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.functions import *


### 1. Creamos la estructura de datos del topic FV

FVSchema = StructType([
            StructField("fecha",StringType(),False),
            StructField("conexiones_inv",FloatType(),False),
            StructField("dias_inv",FloatType(),False),
            StructField("ea_aarr_iii",FloatType(),False),
            StructField("ea_aarr_iiin",FloatType(),False),
            StructField("ea_ayer_inv",FloatType(),False),
            StructField("ea_consumida_inv",FloatType(),False),
            StructField("ea_diaria_inv",FloatType(),False),
            StructField("ea_generada_inv",FloatType(),False),
            StructField("ea_mesactual_inv",FloatType(),False),
            StructField("ea_ultimomes_inv",FloatType(),False),
            StructField("eq_aarr_iii",FloatType(),False),
            StructField("eq_aarr_iiin",FloatType(),False),
            StructField("eq_cap_aarr_iii",FloatType(),False),
            StructField("eq_cap_aarr_iiin",FloatType(),False),
            StructField("eq_ind_aarr_iii",FloatType(),False),
            StructField("eq_ind_aarr_iiin",FloatType(),False),
            StructField("es_aarr_iii",FloatType(),False),
            StructField("es_aarr_iiin",FloatType(),False),
            StructField("estado_inv",StringType(),False),
            StructField("f_aarr",FloatType(),False),
            StructField("fallo_modulo",FloatType(),False),
            StructField("falloactual_inv",StringType(),False),
            StructField("fdp_aarr",FloatType(),False),
            StructField("fdp_inv",FloatType(),False),
            StructField("horas_inv",FloatType(),False),
            StructField("humedad_inv",FloatType(),False),
            StructField("i_aarr_iii",FloatType(),False),
            StructField("i_aarr_l1",FloatType(),False),
            StructField("i_aarr_l2",FloatType(),False),
            StructField("i_aarr_l3",FloatType(),False),
            StructField("i_dc_inv",FloatType(),False),
            StructField("ired_l1_inv",FloatType(),False),
            StructField("ired_l2_inv",FloatType(),False),
            StructField("ired_l3_inv",FloatType(),False),
            StructField("manometro_bt",FloatType(),False),
            StructField("modulos_on_inv",FloatType(),False),
            StructField("n_modulos_inv",FloatType(),False),
            StructField("p_dc_inv",FloatType(),False),
            StructField("pa_aarr_iii",FloatType(),False),
            StructField("pa_aarr_iiin",FloatType(),False),
            StructField("pa_aarr_l1",FloatType(),False),
            StructField("pa_aarr_l2",FloatType(),False),
            StructField("pa_aarr_l3",FloatType(),False),
            StructField("pa_inv",FloatType(),False),
            StructField("pq_inv",FloatType(),False),
            StructField("ps_inv",FloatType(),False),
            StructField("radiacion",FloatType(),False),
            StructField("radiacion1",FloatType(),False),
            StructField("radiacion2",FloatType(),False),
            StructField("regulacion_inv",FloatType(),False),
            StructField("t_admision_inv",FloatType(),False),
            StructField("t_interna_inv",FloatType(),False),
            StructField("tambiente",FloatType(),False),
            StructField("tmax_igbt_inv",FloatType(),False),
            StructField("tmax_modulos_inv",FloatType(),False),
            StructField("tpanel",FloatType(),False),
            StructField("v_aarr_l1",FloatType(),False),
            StructField("v_aarr_l2",FloatType(),False),
            StructField("v_aarr_l3",FloatType(),False),
            StructField("v_bus_dc_inv",FloatType(),False),
            StructField("v_ph_inv",FloatType(),False),
            StructField("vred_l1_inv",FloatType(),False),
            StructField("vred_l2_inv",FloatType(),False),
            StructField("vred_l3_inv",FloatType(),False),
            StructField("years_inv",FloatType(),False),
            StructField("Fecha_s",IntegerType(),False)
            ])


### 2. Creamos un sesion de Spark con todos los workes con 3 Gb de RAM

spark = SparkSession \
    .builder \
    .master('spark://spark-master:7077') \
    .appName("Query by date") \
    .config("spark.executor.memory", "3g") \
    .config("spark.jars.packages","org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0") \
    .getOrCreate()


### 3. Creamos un dataframe donde se guardaran todos los datos del topic FV de Kafka

df = spark \
  .read \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "redpanda:9092") \
  .option("subscribe", "FV") \
  .load()


### 4. Seleccionamos solo la columna valores que esta en formato json, el resto de columnas nos da igual

df1 = df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"),FVSchema).alias("data")).select("data.*")


### 5. Creamos una vista del dataframe para poder realizar una Consulta SQL

df1.createOrReplaceTempView("Photovoltaics")

### 6. Realizamos una query que agrupe los datos por fecha

df1 = spark.sql("""SELECT date(fecha) as date,
            round(max(ea_aarr_iii)-min(ea_aarr_iii),1) as EA_red,
            round(max(es_aarr_iii)-min(es_aarr_iii),1) as ES_red,
            max(ea_diaria_inv) as EA_gen,
            round((max(ea_aarr_iii)-min(ea_aarr_iii))/(max(es_aarr_iii)-min(es_aarr_iii)),2) as FP_red,
            round(max(ea_aarr_iii)-min(ea_aarr_iii) + max(ea_diaria_inv),1) as EA_Consumo
            FROM Photovoltaics
            where ea_aarr_iii > 1000 and es_aarr_iii> 1000
            group by date(fecha)
            order by date(fecha) """)

df1.show()
