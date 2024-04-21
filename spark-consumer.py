import logging
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
from pyspark.sql.functions import col, from_json
from cassandra.cluster import Cluster

def create_keyspace(session):
    session.execute ("""
        CREATE KEYSPACE IF NOT EXISTS property_streams
        WITH replication = {'class':'SimpleStrategy','replication_factor':'1'};      
    """)
    print('Keyspace created successfully')

def create_table(session):
    session.execute("""
        CREATE TABLE IF NOT EXISTS property_streams.properties (
            address text,
            title text,
            link text PRIMARY KEY,
            pictures list<text>,
            floor_plan text
        );
    """)
    print('Table created successfully')

def create_cassandra_session():
    cluster = Cluster(['localhost'])
    session = cluster.connect()
    if session is not None:
        create_keyspace(session)
        create_table(session)
    return session

def insert_data(session, **kwargs):
    print('Inserting data')
    session.execute(
        """
        INSERT INTO property_streams.properties (address, title, link, pictures, floor_plan)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (kwargs['address'], kwargs['title'], kwargs['link'], kwargs['pictures'], kwargs['floor_plan'])
    )
    print('Data inserted')

def main():
    logging.basicConfig(level=logging.INFO)
    spark = SparkSession.builder \
        .appName("RealConsumer") \
        .config("spark.cassandra.connection.host", "localhost") \
        .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.3.0","org.apache.spark:spark-sql-kafka-0-10_2.13:3.3.2") \
        .getOrCreate()

    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "properties") \
        .option("startingOffsets", "earliest") \
        .load()

    schema = StructType([
        StructField("title", StringType(), True),
        StructField("link", StringType(), True),
        StructField("pictures", ArrayType(StringType()), True),
        StructField("floor_plan", StringType(), True),
        StructField("address", StringType(), True)
    ])

    kafka_df = kafka_df.selectExpr("CAST(value AS STRING) as value") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    kafka_df.writeStream \
        .foreachBatch(lambda batch_df, batch_id: batch_df.foreach(lambda row: insert_data(create_cassandra_session(), **row.asDict()))) \
        .start() \
        .awaitTermination()

if __name__ == "__main__":
    main()
