from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import os.path
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

app.run(debug=True)