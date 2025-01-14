from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql.functions import explode,max, min, from_json, col, expr
import logging
import os
from common.common import create_schema_for_iceberg, parse_config
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, FloatType


access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
endpoint = os.getenv("AWS_ENDPOINT")
product_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("description", StringType(), True),
    StructField("price", FloatType(), True)
])

# Define JSON schema
json_schema = StructType([
    StructField("op", StringType(), True),
    StructField("payload", StructType([
        StructField("before", product_schema, True),
        StructField("after", product_schema, True),
    ]), True)
])
# set logger level with format
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

def create_spark_session(endpoint, access_key, secret_key):
    """
    Create a spark session with the given endpoint, access_key, and secret_key
    """
    spark = SparkSession.builder\
    .config("spark.jars.packages","org.apache.hadoop:hadoop-aws:3.5.2,com.amazonaws:aws-java-sdk-bundle:1.11.874,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
    .config("spark.hadoop.fs.s3a.endpoint", endpoint) \
    .config("spark.hadoop.fs.s3a.access.key", access_key) \
    .config("spark.hadoop.fs.s3a.secret.key", secret_key) \
    .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.spark_catalog.type", "hadoop") \
    .config("spark.sql.catalog.spark_catalog.warehouse", "s3a://kafka-streaming/warehouse") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")\
    .config("fs.s3a.metadatastore.impl", "org.apache.hadoop.fs.s3a.s3guard.NullMetadataStore")\
    .appName("kafka-streaming-product")\
    .getOrCreate()
    logging.info("Spark session created successfully with table products")
    return spark
def read_df_from_kafka(spark ,topic_name, bootstrap_server):
    """
    Read data from Kafka
    """
    # df_cdc empty dataframe
    df_cdc = None 
    try:
        df_cdc = spark.readStream.format("kafka") \
            .option("kafka.bootstrap.servers", bootstrap_server) \
            .option("subscribe", topic_name) \
            .option("startingOffsets", "earliest") \
            .option("kafka.security.protocol", "PLAINTEXT") \
            .load()
        logging.info("Reading from Kafka successfully!")
    except Exception as e:
        logging.error(f"Error reading from Kafka: {e}")
    return df_cdc



def transform_funcions(df_cdc):
    """
    Transform data
    """
    # Filter non-null values and parse JSON data
    new_df = df_cdc.filter("value is not null") \
        .withColumn("value", from_json(col("value").cast("string"), json_schema)) \
        .withColumn("cdc_data", expr("case when value.op = 'd' then value.payload.before else value.payload.after end")) \
        .withColumn("is_delete", expr("case when value.op = 'd' then 1 else 0 end")) \
        .withColumn("ver", expr("cast(partition as long) * 100000000000000000 + offset")) \
        .withColumn("timestamp", expr("cast(timestamp as timestamp)")) \
        .select("cdc_data.*", "is_delete", "ver", "value.op", "timestamp")
    return new_df

def load_data_to_s3(df):
    """
    Load data to S3
    """
    # how to write to s3 using iceberg

    try:
        logging.info("Writing to S3 successfully!")
        df.writeStream \
            .format("iceberg") \
            .option("path", "s3a://kafka-streaming/warehouse/default/products") \
            .trigger(processingTime="60 seconds") \
            .outputMode("append") \
            .option("checkpointLocation", "s3a://kafka-streaming/checkpoint") \
            .start()\
            .awaitTermination()
    except Exception as e:
        logging.error(f"Error writing to S3: {e}")


def main():
    """
    Main function
    """
    # read config from file
    file_config = os.path.dirname(os.path.realpath(__file__)) + "/config.yaml"
    config = parse_config(file_config)
    spark = create_spark_session(endpoint, access_key, secret_key)
    df_cdc = read_df_from_kafka(spark, config["topic_name"], config["bootstrap_server"])
    new_df = transform_funcions(df_cdc)
    spark.sql(create_schema_for_iceberg(new_df, "spark_catalog.default.products", "s3a://kafka-streaming/warehouse/default/products"))
    new_df.printSchema()
    load_data_to_s3(new_df)

if __name__ == "__main__":
    main()