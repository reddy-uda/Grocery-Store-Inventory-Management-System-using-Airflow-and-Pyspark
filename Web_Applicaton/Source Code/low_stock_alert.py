from flask import Flask, jsonify
import os
import findspark
import pandas


# Activate PySpark environment
findspark.init()

from pyspark.sql import SparkSession, functions as F

app = Flask(__name__)

# -------------------------------
# Java and Spark setup
# -------------------------------
JAVA_HOME = r"C:\Program Files\Java\jdk-11.0.28"
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PATH"] = JAVA_HOME + r"\bin;" + os.environ["PATH"]

# Path to PostgreSQL JDBC driver
JDBC_DRIVER_PATH = r"C:/spark/custom-jars/postgresql-42.7.8.jar"

# -------------------------------
# Initialize SparkSession ONCE
# -------------------------------
spark = SparkSession.builder \
    .appName("ReadInventoryFromPostgres") \
    .config("spark.driver.extraClassPath", JDBC_DRIVER_PATH) \
    .config("spark.executor.extraClassPath", JDBC_DRIVER_PATH) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# -------------------------------
# JDBC Connection
# -------------------------------
jdbc_url = "jdbc:postgresql://127.0.0.1:5432/postgres"
connection_properties = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

# ---------------- Low Stock Endpoint ----------------
@app.route("/low-stock")
def get_low_stock():
    df = spark.read.jdbc(jdbc_url, "low_stock_data", properties=connection_properties)
    # Select only the required columns
    df = df.select("product_name", "location_name", "category", "quantity", "location_name", "warehouse_name")
    # Convert to Pandas and JSON
    return jsonify(df.toPandas().to_dict(orient="records"))
    # ---------------- Start Flask ----------------
@app.route("/")
def home():
    return "Flask is running!"

if __name__ == "__main__":
    app.run(debug=True)