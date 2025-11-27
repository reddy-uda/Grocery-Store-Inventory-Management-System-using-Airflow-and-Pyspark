from flask import Flask, jsonify
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window




JAVA_HOME = r"C:\Program Files\microsoft-jdk-11.0.28-windows-x64\jdk-11.0.28+6"
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PATH"] = JAVA_HOME + r"\bin;" + os.environ["PATH"]

# Path to your PostgreSQL JDBC driver
JDBC_DRIVER_PATH = r"file:///C:/Users/hrm/Downloads/postgresql-42.7.8.jar"

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

# -------------------------------
# Load Data from PostgreSQL
# -------------------------------
products_df = spark.read.jdbc(jdbc_url, "products", properties=connection_properties)

warehouse_df = spark.read.jdbc(jdbc_url, "warehouse", properties=connection_properties)
warehouse_locations_df=spark.read.jdbc(jdbc_url, "warehouse_locations", properties=connection_properties)
print('warehouse locations..............')
warehouse_locations_df.select('location_name').distinct().show()
inventory_df = spark.read.jdbc(jdbc_url, "inventory", properties=connection_properties)
#
sales_df=spark.read.jdbc(jdbc_url,"product_sales",properties=connection_properties)
print('sales data.........')
sales_df.show()
products_with_inventory=products_df.join(inventory_df,products_df.product_id == inventory_df.product_id,"inner").join(
    warehouse_df,warehouse_df.warehouse_id == inventory_df.warehouse_id,"inner").join(
    warehouse_locations_df,warehouse_locations_df.location_id == warehouse_df.location_id,"inner"

).select(products_df.product_id,
         products_df.product_name,
         inventory_df.quantity,
         inventory_df.warehouse_id,
         warehouse_locations_df.location_name,
         warehouse_df.warehouse_name,
         warehouse_locations_df.created_at)


print('products with inventory...................')
products_with_inventory.show()


inv = inventory_df.alias("inv")

print('checking inventory data.............')

inv.groupBy("product_id").agg(F.countDistinct("warehouse_id").alias("num_warehouses")).show()

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# --- Alias all DataFrames ---
prod = products_df.alias("prod")
inv = inventory_df.alias("inv")
wh = warehouse_df.alias("wh")
loc = warehouse_locations_df.alias("loc")
sales = sales_df.alias("sales")

window_spec = Window.partitionBy("inv.product_id", "inv.warehouse_id").orderBy(F.col("inv.created_at").desc())
inv_latest = inv.withColumn("row_num", F.row_number().over(window_spec)) \
                .filter(F.col("row_num") == 1) \
                .drop("row_num")

# --- Aggregate sales by product and warehouse ---
sales_agg = (sales.groupBy("product_id", "warehouse_id")
                   .agg(
                       F.sum("units_sold").alias("total_units_sold"),
                       F.sum("total_revenue").alias("total_revenue")
                   )
                   .alias("sales_agg"))

# --- Join everything ---
products_with_inventory = (
    prod.join(inv_latest, F.col("prod.product_id") == F.col("inv.product_id"), "left")
        .join(wh, F.col("wh.warehouse_id") == F.col("inv.warehouse_id"), "left")
        .join(loc, F.col("loc.location_id") == F.col("wh.location_id"), "left")
        .join(
            sales_agg,
            (F.col("sales_agg.product_id") == F.col("prod.product_id")) &
            (F.col("sales_agg.warehouse_id") == F.col("wh.warehouse_id")),
            "left"
        )
        .select(
            F.col("prod.product_id"),
            F.col("prod.product_name"),
            F.col("prod.cost_price"),
            F.col("prod.category"),
            F.col("prod.selling_price"),
            F.col("inv.quantity"),
            F.col("wh.warehouse_id"),
            F.col("wh.warehouse_name"),
            F.col("wh.warehouse_address"),
            F.col("loc.location_name"),
            F.col("sales_agg.total_units_sold"),
            F.col("sales_agg.total_revenue"),
            F.col("inv.created_at").alias("inventory_created_at")
        )
)

products_with_inventory.show(truncate=False)


"""Current stock"""

print('unique locations...........')

products_with_inventory.select('location_name').distinct().show()

products_with_inventory.write.jdbc(
    url=jdbc_url,
    table="current_stock",
    properties=connection_properties,
    mode="overwrite"
)
#
print('current stock is saved in postgres')

""" Low stocks"""


LOW_STOCK_THRESHOLD = 50

low_stock_df= products_with_inventory.filter(F.col('quantity') <= LOW_STOCK_THRESHOLD)

print('low stock data')
low_stock_df.show()

window_spec = Window.partitionBy("product_id", "warehouse_id").orderBy(F.col("inventory_created_at").desc())

latest_inventory_df = (
    low_stock_df
    .withColumn("row_num", F.row_number().over(window_spec))
    .filter(F.col("row_num") == 1)
    .drop("row_num")
)


print("low stock data...........")
latest_inventory_df.show()

latest_inventory_df.write.jdbc(
    url=jdbc_url,
    table="low_stock_data",
    properties=connection_properties,
    mode="overwrite"
)

#
print('low stock data is written to low_stock_data')

""" Inventory aging data"""

all_inventory_df = (
    prod.join(inv, F.col("prod.product_id") == F.col("inv.product_id"), "left")
        .join(wh, F.col("wh.warehouse_id") == F.col("inv.warehouse_id"), "left")
        .join(loc, F.col("loc.location_id") == F.col("wh.location_id"), "left")
        .join(
            sales_agg,
            (F.col("sales_agg.product_id") == F.col("prod.product_id")) &
            (F.col("sales_agg.warehouse_id") == F.col("wh.warehouse_id")),
            "left"
        )
        .select(
            F.col("prod.product_id"),
            F.col("prod.product_name"),
            F.col("prod.cost_price"),
            F.col("prod.selling_price"),
            F.col("inv.quantity"),
            F.col("wh.warehouse_id"),
            F.col("wh.warehouse_name"),
            F.col("wh.warehouse_address"),
            F.col("loc.location_name"),
            F.col("sales_agg.total_units_sold"),
            F.col("sales_agg.total_revenue"),
            F.col("inv.created_at").alias("inventory_created_at")
        )
)

print('all inventory data.............')
all_inventory_df.show()
today=F.current_date()
inventory_with_age=all_inventory_df.withColumn(
    "aging_days",F.datediff(today,F.to_date("inventory_created_at"))
)

inventory_with_bucket = inventory_with_age.withColumn(
    "aging_bucket",
    F.when(F.col("aging_days") <= 30, "0–30 Days")
     .when((F.col("aging_days") > 30) & (F.col("aging_days") <= 60), "31–60 Days")
     .when((F.col("aging_days") > 60) & (F.col("aging_days") <= 90), "61–90 Days")
     .otherwise("90+ Days")
)
inventory_aging_summary = (
    inventory_with_bucket
    .groupBy("product_id", "aging_bucket")
    .agg(F.sum("quantity").alias("total_quantity"))
)

products_with_aging = inventory_aging_summary.join(
    products_df, "product_id", "left"
)
print('products with aging......................')
products_with_aging.show()

products_with_aging.write.jdbc(
    url=jdbc_url,
    table="inventory_aging_data",
    properties=connection_properties,
    mode="overwrite"
)

print("inventory aging data is written")


