# File: dags/api_integration_dag.py


from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from faker import Faker
import psycopg2
import random


fake = Faker()


def insert_inventory_data(**kwargs):
    """
    Fetch product data from a dummy API, generate fake inventory,
    suppliers, warehouses, and insert into Postgres.
    """
    try:
        # Connect to Postgres
        conn = psycopg2.connect(
            host="new-airflow-r_a584e0-postgres-1",
            port=5432,
            database="postgres",
            user="postgres",
            password="postgres"
        )
        cur = conn.cursor()


        # --- Fetch products from API ---
        def fetch_products_from_api(limit=20):
            try:
                response = requests.get(f"https://dummyjson.com/products?limit={limit}", timeout=10)
                response.raise_for_status()
                return response.json().get("products", [])
            except Exception as e:
                print(f"❌ API request failed: {e}")
                return []


        api_products = fetch_products_from_api(limit=20)


        if not api_products:
            print("⚠️ No products fetched, skipping insertion.")
            return


        # --- Insert warehouse locations ---
        for _ in range(3):
            cur.execute(
                "INSERT INTO warehouse_locations (location_name) VALUES (%s) ON CONFLICT DO NOTHING;",
                (fake.city(),)
            )


        # --- Insert warehouses ---
        for _ in range(3):
            cur.execute(
                "INSERT INTO warehouse (warehouse_name, warehouse_address, location_id) VALUES (%s, %s, %s);",
                (fake.company(), fake.address(), random.randint(1, 3))
            )


        # --- Insert suppliers ---
        for _ in range(5):
            cur.execute(
                "INSERT INTO suppliers (supplier_name, supplier_address) VALUES (%s, %s);",
                (fake.company(), fake.address())
            )


        # --- Insert products ---
        for product in api_products:
            product_name = product["title"]
            sku = f"SKU-{product['id']:05d}"
            category = product.get("category", "General").capitalize()
            selling_price = float(product.get("price", random.uniform(50, 500)))
            cost_price = round(selling_price * random.uniform(0.6, 0.9), 2)
            unit = random.choice(["pcs", "kg", "ltr"])
            lead_time = random.randint(1, 14)


            cur.execute(
                """
                INSERT INTO products (product_name, sku, category, cost_price, selling_price, unit, lead_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sku) DO NOTHING;
                """,
                (product_name, sku, category, cost_price, selling_price, unit, lead_time)
            )


        # --- Link products with suppliers ---
        for _ in range(15):
            cur.execute(
                "INSERT INTO product_suppliers (product_id, supplier_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (random.randint(1, len(api_products)), random.randint(1, 5))
            )


        # --- Insert inventory records ---
        for _ in range(20):
            cur.execute(
                "INSERT INTO inventory (product_id, warehouse_id, quantity) VALUES (%s, %s, %s);",
                (random.randint(1, len(api_products)), random.randint(1, 3), random.randint(10, 500))
            )


        # --- Insert product sales ---
        for _ in range(30):
            product_id = random.randint(1, len(api_products))
            warehouse_id = random.randint(1, 3)
            sale_date = fake.date_between(start_date="-30d", end_date="today")
            units_sold = random.randint(1, 50)


            cur.execute("SELECT selling_price FROM products WHERE product_id = %s;", (product_id,))
            price_row = cur.fetchone()
            unit_price = price_row[0] if price_row else random.uniform(100, 400)


            cur.execute(
                """
                INSERT INTO product_sales (product_id, warehouse_id, sale_date, units_sold, unit_price)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (product_id, warehouse_id, sale_date, units_sold, unit_price)
            )


        conn.commit()
        cur.close()
        conn.close()
        print("✅ Inventory data inserted successfully.")


    except Exception as e:
        print("❌ Error inserting data:", e)
        raise


# === Define DAG ===
with DAG(
    dag_id="api_integration",
    start_date=datetime(2025, 10, 16),   # Use past date to ensure DAG registers
    schedule="* * * * *",
    catchup=False,
    tags=["astro"],
    max_active_runs=1,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=5)
    }
) as dag:


    insert_inventory_task = PythonOperator(
        task_id="insert_inventory_task",
        python_callable=insert_inventory_data
    )



