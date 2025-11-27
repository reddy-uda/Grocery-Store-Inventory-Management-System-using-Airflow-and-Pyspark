from flask import Flask, jsonify
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window




JAVA_HOME = r"path/to/your/jdk-11.0.28"
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PATH"] = JAVA_HOME + r"\bin;" + os.environ["PATH"]

# Path to your PostgreSQL JDBC driver
JDBC_DRIVER_PATH = "file:///path/to/your/postgresql-driver.jar"

spark = SparkSession.builder \
    .appName("SalesManagerDashboard") \
    .config("spark.jars", JDBC_DRIVER_PATH) \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")
# PostgreSQL connection
jdbc_url = "jdbc:postgresql://127.0.0.1:5432/postgres"
connection_properties = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

spark = SparkSession.builder.getOrCreate()
df = spark.range(1).select(F.current_date().alias("today"))
df.show()

from pyspark.sql import functions as F

products_df = spark.read.jdbc(jdbc_url, "products", properties=connection_properties)

warehouse_df = spark.read.jdbc(jdbc_url, "warehouse", properties=connection_properties)
warehouse_locations_df=spark.read.jdbc(jdbc_url, "warehouse_locations", properties=connection_properties)
print('warehouse locations..............')
warehouse_locations_df.select('location_name').distinct().show()
inventory_df = spark.read.jdbc(jdbc_url, "inventory", properties=connection_properties)
#
sales_df=spark.read.jdbc(jdbc_url,"product_sales",properties=connection_properties)

prod = products_df.alias("prod")
inv = inventory_df.alias("inv")
wh = warehouse_df.alias("wh")
loc = warehouse_locations_df.alias("loc")
sales = sales_df.alias("sales")


from pyspark.sql import functions as F

merged_df = (
    inv
    .join(prod, F.col("inv.product_id") == F.col("prod.product_id"), "left")
    .join(wh, F.col("inv.warehouse_id") == F.col("wh.warehouse_id"), "left")
    # FIX: join warehouse_locations via location_id, not warehouse_id
    .join(loc, F.col("wh.location_id") == F.col("loc.location_id"), "left")
    .join(
        sales,
        (
            (F.col("inv.product_id") == F.col("sales.product_id")) &
            (F.col("inv.warehouse_id") == F.col("sales.warehouse_id")) &
            (F.to_date(F.col("inv.created_at")) == F.to_date(F.col("sales.created_at")))
        ),
        "left"
    )
)

from pyspark.sql import functions as F

sales_agg_df = (
    merged_df
    # create a date-only column from inv.created_at
    .withColumn("date_only", F.to_date("inv.created_at"))
    .groupBy(
        "inv.warehouse_id",
        "wh.warehouse_name",         # warehouse name
        "inv.product_id",
        "prod.product_name",         # product name
        "prod.category",             # product category
        "date_only"
    )
    .agg(
        F.sum("inv.quantity").alias("total_inventory_qty"),
        F.sum("sales.units_sold").alias("total_sales_qty"),
        F.sum(F.col("inv.quantity") * F.col("sales.unit_price")).alias("inventory_value"),
        F.avg("sales.unit_price").alias("avg_unit_price")  # average unit price
    )
    .orderBy("inv.warehouse_id", "date_only", "prod.product_name")
)




sales_agg_df.write.jdbc(
    url=jdbc_url,
    table="sales_aggregated_data",
    properties=connection_properties,
    mode="overwrite"
)

print('aggregated sales data is saved.')

