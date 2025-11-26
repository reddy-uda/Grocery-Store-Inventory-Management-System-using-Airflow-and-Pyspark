from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime


with DAG(
    dag_id="refresh_inventory_tables_dag",
    start_date=datetime(2025, 10, 11),
    schedule=None,  # Run manually before loading fake data
    catchup=False,
    tags=["postgres", "inventory", "setup"]
) as dag:
    # Drop existing tables if any
    drop_tables = SQLExecuteQueryOperator(
        task_id="clear_tables",
        split_statements=True,
        conn_id="my_postgres_conn",  # Airflow Postgres connection
        sql="""
        DROP TABLE IF EXISTS inventory CASCADE;
        DROP TABLE IF EXISTS product_suppliers CASCADE;
        DROP TABLE IF EXISTS products CASCADE;
        DROP TABLE IF EXISTS suppliers CASCADE;
        DROP TABLE IF EXISTS warehouse CASCADE;
        DROP TABLE IF EXISTS warehouse_locations CASCADE;
        DROP TABLE IF EXISTS product_sales CASCADE;
        DROP TABLE IF EXISTS product_sales_summary CASCADE;
        DROP TABLE IF EXISTS warehouse_performance CASCADE;
        DROP TABLE IF EXISTS inventory_value_summary CASCADE;
        DROP TABLE IF EXISTS supplier_dependency_analysis CASCADE;
        """
    )


    # Recreate tables
    create_tables = SQLExecuteQueryOperator(
        task_id="create_tables",
        conn_id="my_postgres_conn",
        split_statements=True,
        sql="""
        CREATE TABLE warehouse_locations (
    location_id SERIAL PRIMARY KEY,
    location_name VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE warehouse (
    warehouse_id SERIAL PRIMARY KEY,
    warehouse_name VARCHAR(255) UNIQUE,
    warehouse_address VARCHAR(255),
    location_id INT REFERENCES warehouse_locations(location_id),
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(255) UNIQUE,
    supplier_address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) UNIQUE,
    sku VARCHAR(255) UNIQUE,
    category VARCHAR(255),
    cost_price DECIMAL(10,2),
    selling_price DECIMAL(10,2),
    unit VARCHAR(255),
    lead_time INT,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE product_suppliers (
    product_id INT REFERENCES products(product_id),
    supplier_id INT REFERENCES suppliers(supplier_id),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (product_id, supplier_id)
);


CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id),
    warehouse_id INT REFERENCES warehouse(warehouse_id),
    quantity INT,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE product_sales (
    sale_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id),
    warehouse_id INT REFERENCES warehouse(warehouse_id),
    sale_date DATE NOT NULL,
    units_sold INT CHECK (units_sold >= 0),
    created_at TIMESTAMP DEFAULT NOW(),
    unit_price DECIMAL(10,2) CHECK (unit_price >= 0),
    total_revenue DECIMAL(10,2) GENERATED ALWAYS AS (units_sold * unit_price) STORED
        );


        """
    )
       


    drop_tables >> create_tables



