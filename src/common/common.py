
from pyspark.sql import DataFrame
import logging

def create_schema_for_iceberg(df:DataFrame,table_name:str,path_data:str):
    """
    mapping data type from spark to iceberg 
    return sql string 
    """
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    for field in df.schema.fields:
        sql += f"{field.name} {mapping_data_type_to_iceberg(str(field.dataType))},"
    sql += f""") USING iceberg LOCATION "{path_data}" """
    # how to remove , end of string
    sql = sql.replace(",)",")")
    return sql

def mapping_data_type_to_iceberg(spark_data_type:str):
    logging.info(f"Mapping data type from spark to iceberg: {spark_data_type}")
    spark_data_type = spark_data_type.replace("()","")
    if spark_data_type == "LongType":
        return "LONG"
    if spark_data_type == "IntegerType":
        return "INT"
    if spark_data_type == "StringType":
        return "STRING"
    if spark_data_type == "FloatType":
        return "FLOAT"
    if spark_data_type == "TimestampType":
        return "TIMESTAMP"
    return None


def parse_config(config_file:str):
    """
    Parse config file
    """
    config = {}
    with open(config_file, "r") as file:
        for line in file:
            key, value = line.split("=")
            config[key.strip()] = value.strip()
    return config