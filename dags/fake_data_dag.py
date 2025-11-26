from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from faker import Faker
import psycopg2
import random

fake = Faker()

def insert_inventory_data():
    try:
        # Connect to Postgres (existing container)
        conn = psycopg2.connect(
            host="new-airflow-r_a584e0-postgres-1",  # your Postgres container name 
            port=5432,
            database="postgres",  # your database
            user="postgres",
            password="postgres"
        )
        cur = conn.cursor()

        # Insert fake warehouse locations
        for _ in range(3):
            cur.execute(
                "INSERT INTO warehouse_locations (location_name) VALUES (%s) ON CONFLICT DO NOTHING;",
                (fake.city(),)
            )

        # Insert fake warehouses
        for _ in range(3):
            cur.execute(
                "INSERT INTO warehouse (warehouse_name, warehouse_address, location_id) VALUES (%s, %s, %s);",
                (fake.company(), fake.address(), random.randint(1, 3))
            )

        # Insert fake suppliers
        for _ in range(5):
            cur.execute(
                "INSERT INTO suppliers (supplier_name, supplier_address) VALUES (%s, %s);",
                (fake.company(), fake.address())
            )

        # Insert fake products
        for _ in range(10):
            cur.execute(
                """
                INSERT INTO products (product_name, sku, category, cost_price, selling_price, unit, lead_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    fake.word().capitalize(),
                    fake.unique.bothify(text="SKU-#####"),
                    random.choice(["Electronics", "Furniture", "Food", "Toys"]),
                    round(random.uniform(10, 200), 2),
                    round(random.uniform(200, 400), 2),
                    random.choice(["pcs", "kg", "ltr"]),
                    random.randint(1, 14)
                )
            )

        # Link products with suppliers
        for _ in range(10):
            cur.execute(
                "INSERT INTO product_suppliers (product_id, supplier_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (random.randint(1, 10), random.randint(1, 5))
            )

        # Insert inventory records
        for _ in range(20):
            cur.execute(
                "INSERT INTO inventory (product_id, warehouse_id, quantity) VALUES (%s, %s, %s);",
                (random.randint(1, 10), random.randint(1, 3), random.randint(1, 500))
            )

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Fake inventory data inserted successfully.")

    except Exception as e:
        print("❌ Error inserting data:", e)
        raise


with DAG(
    dag_id="insert_fake_inventory_dag",
    start_date=datetime(2025, 10, 16),
    schedule="* * * * *",  # every minute
    catchup=False,
    tags=["postgres", "faker", "inventory"]
) as dag:

    insert_data_task = PythonOperator(
        task_id="insert_fake_inventory",
        python_callable=insert_inventory_data
    )

