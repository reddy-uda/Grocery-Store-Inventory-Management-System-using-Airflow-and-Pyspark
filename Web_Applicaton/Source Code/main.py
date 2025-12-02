from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
import os.path
from Mail import send_email

conn = pymysql.connect(host="localhost", user="root", password="sai@54321", db="ml_inventory")
cursor = conn.cursor()
app = Flask(__name__)
app.secret_key = "abc"
admin_username = "admin"
admin_password = "admin"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/store_manager_login")
def store_manager_login():
    return render_template("store_manager_login.html")


@app.route("/store_manager_registration_action", methods=['POST'])
def store_manager_registration_action():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    store_name = request.form.get("store_name")
    address = request.form.get("address")
    location = request.form.get("location")

    # --- Check for duplicate entries ---
    count = cursor.execute("SELECT * FROM store_manager WHERE email=%s OR phone=%s", (email, phone))
    if count > 0:
        return redirect("/store_manager_login?message=Duplicate Details Exist")
    else:
        # --- Insert new store manager record ---
        cursor.execute("""
            INSERT INTO store_manager(name, email, phone, password, store_name, address, location)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, phone, password, store_name, address, location))
        conn.commit()
        return redirect("/store_manager_login?message=Store Manager Registered Successfully")


@app.route("/store_manager_login_action", methods=["POST"])
def store_manager_login_action():
    email = request.form.get("email")
    password = request.form.get("password")

    count = cursor.execute("SELECT * FROM store_manager WHERE email=%s AND password=%s", (email, password))
    if count > 0:
        store_manager = cursor.fetchall()
        session['store_manager_id'] = store_manager[0][0]
        session['role'] = 'store_manager'
        return redirect("/store_manager_home")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/inventory_manager_login")
def inventory_manager_login():
    return render_template("inventory_manager_login.html")


@app.route("/inventory_manager_registration_action", methods=['POST'])
def inventory_manager_registration_action():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    department = request.form.get("department")
    address = request.form.get("address")
    location = request.form.get("location")

    # --- Check for duplicate entries ---
    count = cursor.execute("SELECT * FROM inventory_manager WHERE email=%s OR phone=%s", (email, phone))
    if count > 0:
        return redirect("/inventory_manager_login?message=Duplicate Details Exist")
    else:
        # --- Insert new inventory manager record ---
        cursor.execute("""
            INSERT INTO inventory_manager(name, email, phone, password, department, address, location)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, phone, password, department, address, location))
        conn.commit()
        return redirect("/inventory_manager_login?message=Inventory Manager Registered Successfully")


@app.route("/inventory_manager_login_action", methods=["POST"])
def inventory_manager_login_action():
    email = request.form.get("email")
    password = request.form.get("password")

    count = cursor.execute("SELECT * FROM inventory_manager WHERE email=%s AND password=%s", (email, password))
    if count > 0:
        inventory_manager = cursor.fetchall()
        session['inventory_manager_id'] = inventory_manager[0][0]
        session['role'] = 'inventory_manager'
        return redirect("/inventory_manager_home")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/inventory_manager_home")
def inventory_manager_home():
    return render_template("inventory_manager_home.html")


@app.route("/store_manager_home")
def store_manager_home():
    return render_template("store_manager_home.html")



import findspark
import pandas


# Activate PySpark environment
findspark.init()

from pyspark.sql import SparkSession, functions as F



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



@app.route("/low-stock")
def get_low_stock():
    # 1. Check session
    inventory_manager_id = session.get("inventory_manager_id")
    if not inventory_manager_id:
        return jsonify({"error": "Unauthorized access"}), 401

    # 2. Fetch low stock data
    df = spark.read.jdbc(jdbc_url, "low_stock_data", properties=connection_properties)

    df = df.select("product_name", "location_name", "category",
                   "quantity", "warehouse_name")

    low_stock_pd = df.toPandas()
    low_stock_list = low_stock_pd.to_dict(orient="records")

    # 3. Fetch manager details
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, email
        FROM inventory_manager
        WHERE inventory_manager_id = %s
    """, (inventory_manager_id,))
    manager = cursor.fetchone()

    if not manager:
        return jsonify({"error": "Manager not found"}), 404

    manager_name = manager[0]
    manager_email = manager[1]

    # 4. Convert DataFrame to HTML table
    if not low_stock_pd.empty:
        table_html = low_stock_pd.to_html(
            index=False,
            justify="center",
            border=1,
            classes="table-style"
        )
    else:
        table_html = "<p>No low stock items found.</p>"

    # 5. Prepare HTML Email
    email_subject = "📦 Low Stock Alert - Inventory Report"

    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">

        <p>Dear <b>{manager_name}</b>,</p>

        <p style="font-size: 15px;">
            🔔 <b>Low Stock Alert!</b><br>
            The following items have reached a <b>critical low stock level</b>:
        </p>

        <!-- Styled Table Wrapper -->
        <div style="
            margin: 20px auto;
            padding: 10px;
            width: 85%;
            max-width: 650px;
            background: #fafafa;
            border: 1px solid #ddd;
            border-radius: 8px;
        ">
            <!-- APPLY INLINE STYLING TO TABLE GENERATED BY Pandas -->
            <div style="
                overflow-x: auto;
            ">
                {table_html.replace('<table', '<table style="border-collapse: collapse; width: 100%; font-size: 13px;"')
        .replace('<th', '<th style="border: 1px solid #ccc; padding: 6px; background:#f2f2f2; text-align:center;"')
        .replace('<td', '<td style="border: 1px solid #ccc; padding: 6px; text-align:center;"')}
            </div>
        </div>

        <p>Please take necessary action to avoid supply interruptions.</p>

        <p>Best Regards,<br>
        <b>Inventory Management System 🤖</b></p>

    </body>
    </html>
    """

    send_email(email_subject, email_body, manager_email)

    return render_template("message_action.html",
                           message=" Low Stock Alert Email Sent Successfully! Please check your inbox.")

app.run(debug=True)