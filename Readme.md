### **Grocery Store Inventory Management System**

The Grocery Store Inventory Management System is a fully automated data pipeline that collects, processes, and analyzes retail inventory and sales data using Airflow, PostgreSQL, PySpark, and Power BI. It delivers real-time insights through dashboards, and a web application allows authorized managers to securely log in and view these reports online.

**Table of contents**

1. [Project focus](#project-focus)  
2. [Architecture](#architecture)  
3. [Tools and Technologies](#requirements)
4. [Getting started](#getting-started)  
5. [Installation](#installation)  
6. [Airflow Folder Overview](#airflow-folder-overview)  
7. [User Interface of Airflow](#user-interface-of-airflow)  
8. [Data Processing using Pyspark](#data-processing-using-pyspark)  
9. [Power BI Integration](#power-bi-integration) 
10. [Web Application](#web-application)

## **Project focus**

This project is centered on building a fully automated Retail Data Pipeline that combines Apache Airflow, PostgreSQL, PySpark, and Power BI to manage retail inventory and sales data in a seamless and dependable way. The aim is to create a system that can continuously bring in fresh data, clean and organize it, perform analytics, and make insights instantly available without needing manual involvement.

Apache Airflow acts as the orchestrator. With deployment handled through Astronomer, all workflows such as table creation, scheduled ingestion, and routine transformations run smoothly and consistently. The DAGs are designed to reflect real retail operations, where data updates happen frequently and need timely processing.

PostgreSQL serves as the main database, structured around products, suppliers, warehouses, inventory changes, and sales transactions. The schema is organized to support fast queries and accurate reporting.

PySpark manages the transformation and analytics layer. It loads raw data from PostgreSQL, applies cleaning rules, performs joins, and generates insights like low-stock alerts, inventory aging, stock value, ABC classification, and sales performance. These results are pushed back into PostgreSQL for dashboard consumption.

Power BI connects to these processed tables to create visual reports on stock status, sales trends, and warehouse performance.

Additionally, MySQL is used in the web application layer specifically for handling user registrations and logins, ensuring secure and efficient authentication.

Overall, the project delivers a scalable and production-ready solution for real retail analytics.

## **Architecture**   
     
   ![Architecture](https://raw.githubusercontent.com/reddy-uda/Grocery-Store-Inventory-Management-System-using-Airflow-and-Pyspark/master/images/architecture.png)
  

## **Requirements**  
   This project brings together a set of tools that work smoothly across different parts of the data pipeline. Each technology is used for a specific purpose, and together they help the system run reliably from end to end.

**Workflow & Automation**

* Apache Airflow \- Used as the main scheduler to run all data workflows automatically.  
* Astronomer \- Helps deploy Airflow in a stable environment and makes managing pipelines easier.

**Databases**

* PostgreSQL \- Stores all retail-related data, including raw records, transformed tables, and analytical outputs.  
* MySQL \- Used separately in the web application for handling user registrations and login authentication.

**Data Processing**

* PySpark \- Handles heavy processing tasks such as cleaning data, joining tables, and calculating inventory and sales metrics.  
* Python \- Used across the project for building Airflow DAGs, writing scripts, and connecting different components.  
* Faker / DummyJSON APIs \- Generate synthetic retail data to simulate real-world input.

  	DummyJSON API Source: [https://dummyjson.com/products](https://dummyjson.com/products)

**Dashboards & Reporting**

* Power BI \- Converts the processed data into dashboards and KPIs, making it easier to understand stock levels and sales performance.

**Development & Environment**

* Git & GitHub \- Used for version control and managing project code.  
* VS Code / PyCharm \- IDEs used for writing and organizing the project’s Python scripts.  
* JDBC Drivers \- Enable Spark to connect and communicate with PostgreSQL.


## **Getting started**

This project is meant to guide you through setting up and running an automated retail data pipeline from the ground up. Before working with the workflows, you’ll need to install a few essential tools, including Python, Airflow, PostgreSQL, and PySpark. The next section walks you through the installation process step by step. Once everything is installed, you can clone the project, look through the folder structure, and get familiar with the DAGs, database design, and transformation scripts to see how each part fits together. After the setup is complete, you can start running the DAGs and connect Power BI to view the generated insights.


## **Installation**

To set up the required tools and prepare your environment for this project, please refer to the **installation.md** file included in the repository. It provides step-by-step instructions for installing Python, Airflow, PostgreSQL, PySpark, and all other dependencies needed to run the pipeline.

The guide also explains how to configure the necessary environment variables, create database connections, and prepare your system for running the DAGs smoothly. Make sure to follow the installation document before moving ahead with the workflow execution.


## **Airflow Folder Overview**

This project uses a few key files that are essential for running the Airflow-based retail data pipeline. Below is a short explanation of only the parts that matter for the workflow which are in the “Air\_Flow” Folder.

**DAG Files (Core Workflow Logic)**

These files control how data flows through the pipeline.

* **api\_integration\_dag.py**  
   The main DAG for pulling synthetic retail data and inserting it into PostgreSQL. It handles data ingestion and runs at regular intervals.

* **refresh\_tables\_dag.py**  
   Creates and refreshes all the database tables. This is usually triggered during setup or when you want to reset the schema.

**PostgreSQL Database Schema:**
![DataBase](https://raw.githubusercontent.com/reddy-uda/Grocery-Store-Inventory-Management-System-using-Airflow-and-Pyspark/master/images/Database.png)

**docker-compose.yml**

The most important file for bringing up Airflow, PostgreSQL, and other services. Running `docker-compose up` starts the entire environment.

 **Dockerfile**

Defines custom configurations for the Airflow image, including extra Python packages required by the DAGs.

 **airflow\_settings.yaml**

Stores Airflow connections and variables. Importing this file sets up required connections (like PostgreSQL) automatically.

 **.env**

Contains environment variables such as PostgreSQL and Airflow credentials. Both Docker and Airflow read from this file.

 **postgresql.conf & pg\_hba.conf**

Configuration files are used to adjust PostgreSQL behavior and authentication rules (mainly for local setup).

 **requirements.txt**

Lists Python libraries needed for Airflow, PostgreSQL connections, PySpark integration, and utility scripts.

## **User Interface of Airflow**

Airflow is used to schedule and manage all the workflows in this project. The initial Airflow setup was created using the command `astro dev init`. This step is already completed, so **do not run this command again** after cloning the project.

Once the environment is ready, you can start Airflow using Astronomer. When you run the command:

`astro dev start`

The project starts building… . After building, Astronomer automatically launches Airflow and sets up the web interface for you. After a few seconds, Airflow becomes available in your browser at:

`http://localhost:8080`

 Before running any DAG, make sure to **add the PostgreSQL connection** in the **Admin → Connections** tab inside the Airflow UI. This allows the DAGs to communicate with the database.

 **DAGs Location**

All workflow files are stored inside the `dags/` folder. Airflow automatically detects any DAG placed in this directory and displays it in the UI.

`Air-Flow-folder/`

`│── dags/`

`│    ├── api_integration_dag.py`

`│    └── refresh_tables_dag.py`

### **Airflow UI**

**Home Tab:** This page provides an overview of the Airflow environment, showing system status, recent tasks, and general workflow activity.

![Airflow Home](https://raw.githubusercontent.com/reddy-uda/Grocery-Store-Inventory-Management-System-using-Airflow-and-Pyspark/master/images/Airflow_home.png)

**DAGs Tab:** This page shows all available DAGs, their schedules, status, and whether they are active.

![Dag tab](https://raw.githubusercontent.com/reddy-uda/Grocery-Store-Inventory-Management-System-using-Airflow-and-Pyspark/master/images/dagtab.png)

 **referesh\_inventory\_ tables DAG**

![Refresh_dag](https://raw.githubusercontent.com/reddy-uda/Grocery-Store-Inventory-Management-System-using-Airflow-and-Pyspark/master/images/Refresh.png)


In this view, you can monitor recent DAG runs, check their status, review execution details, and explore logs for each task.

## **Data Processing using Pyspark**

PySpark is used in this project to handle all the heavy data processing tasks. Once Airflow ingests the raw inventory and sales data into PostgreSQL, PySpark loads these tables, processes them, and prepares the cleaned and aggregated outputs that will later be used in Power BI.

The PySpark processing scripts are stored inside the project:

`PySpark/spark_analysis.py`

`PySpark/powerbi.py`

These scripts can be triggered through an Airflow DAG or run manually during development. Each script connects to PostgreSQL using JDBC and loads the required raw tables into Spark DataFrames.

Inside the PySpark scripts, the following operations take place:

* Cleaning and formatting raw data

* Joining tables such as products, suppliers, warehouses, inventory, and sales

* Calculating metrics like low-stock items, stock aging, stock value, and sales-related indicators

* Preparing aggregated inventory and sales summaries

* Creating optimized analytics tables specifically designed for Power BI dashboards

Once the transformations are complete, PySpark writes the final processed results back into PostgreSQL, storing them in dedicated analytics tables that Power BI can read directly.

## **Power BI Integration**

Power BI is used in this project to transform the processed PostgreSQL data into clear and interactive dashboards. The repository includes a ready-made Power BI reports named **Inventory\_Dashboard.pbix**, **Sales\_Dashboard.pbix** which are designed to connect directly to the analytics tables generated by PySpark. After the data pipeline runs, PySpark loads all cleaned and aggregated data back into PostgreSQL, and this becomes the source for the Power BI visuals.

When you open either dashboard file for the first time, Power BI will ask you to update the PostgreSQL connection details, including the host, port, database name, username, and password. After entering the correct values, the dashboards refresh and display the latest results. All insights—such as current stock levels, aging inventory, fast- and slow-moving items, total sales, revenue trends, and warehouse-wise performance—are directly pulled from the updated PostgreSQL tables.

 **Inventory Dashboard**

![Inventory_dashboard](https://raw.githubusercontent.com/reddy-uda/Grocery-Store-Inventory-Management-System-using-Airflow-and-Pyspark/master/images/Inventory_Dashboard.png)
  
 This dashboard highlights product availability, low-stock alerts, aging analysis, stock valuation, and overall inventory performance.

 **Sales Dashboard**

![Sales_dashboard](https://raw.githubusercontent.com/reddy-uda/Grocery-Store-Inventory-Management-System-using-Airflow-and-Pyspark/master/images/Sales_Dashboard.png)

This dashboard visualizes sales trends, daily/weekly performance, top-selling products, revenue distribution, and warehouse-level sales insights.

Together, these dashboards allow managers to monitor the real-time output of the pipeline and make informed business decisions based on up-to-date analytics.

## **Web application**

The project also includes a simple web application that allows inventory and sales managers to access the Power BI dashboard in a secure and organized way. The application uses MySQL to handle user registration and login, ensuring that only authorized managers can view sensitive business insights. Before running the application, the MySQL database must be loaded using the script provided in the **Web\_Application/Database/** folder. The main application logic runs from **Web\_Application/source\_code/main.py**, which handles the routing, authentication, and dashboard display.

Once a manager creates an account and logs in, they are taken to a dedicated page where the embedded Power BI dashboard is displayed. This makes it easy for users to view inventory trends, sales performance, low-stock alerts, and other key metrics directly from the browser without needing to open Power BI Desktop.

The web app acts as a front-end layer that combines authentication, user access control, and data visualization. This setup provides a convenient and centralized place for operational teams to monitor the real-time output of the data pipeline.

