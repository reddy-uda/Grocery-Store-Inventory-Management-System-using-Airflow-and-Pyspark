1. ##  **Install Required Software**

### **Docker**

Download and install Docker Desktop for Windows:  
 [https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)

### **Astronomer CLI**

Install the Astronomer CLI for Windows (Widget Installer):  
 [https://www.astronomer.io/docs/astro/cli/install-cli](https://www.astronomer.io/docs/astro/cli/install-cli)

### **JDK 11**

Download and install JDK 11.0.28  
 [https://aka.ms/download-jdk/microsoft-jdk-11.0.28-windows-x64.zip](https://aka.ms/download-jdk/microsoft-jdk-11.0.28-windows-x64.zip)

### **Python 3.10**

Install Python 3.10 from the official source:  
 [https://www.python.org/downloads/release/python-3100/](https://www.python.org/downloads/release/python-3100/)

### **Apache Spark**

Download Spark 3.5.7 (Hadoop 3 build):  
 [https://www.apache.org/dyn/closer.lua/spark/spark-3.5.7/spark-3.5.7-bin-hadoop3.tgz](https://www.apache.org/dyn/closer.lua/spark/spark-3.5.7/spark-3.5.7-bin-hadoop3.tgz)

Extract Spark and place it in your preferred directory, for example:

`C:\spark\spark-3.5.7-bin-hadoop3`

### **Hadoop (Winutils)**

Download the Hadoop winutils binary:  
 [https://github.com/cdarlint/winutils/blob/master/hadoop-3.3.6/bin/winutils.exe](https://github.com/cdarlint/winutils/blob/master/hadoop-3.3.6/bin/winutils.exe)

Place the `winutils.exe` inside your Hadoop directory.

2. ##  **Set Environment Variables**

Open **System Properties > Advanced > Environment Variables**  
 and add the following **System Variables**:

### **System Variables**

| Variable Name | Value |
| ----- | ----- |
| SPARK\_HOME | C:\\spark\\spark-3.5.7-bin-hadoop3 |
| HADOOP\_HOME | C:\\hadoop |
| PYSPARK\_PYTHON | C:\\path\\to\\your\\Programs\\Python\\Python310\\python.exe |
| JAVA\_HOME | C:\\Program Files\\Java\\jdk-11.0.28 |

3. ## **Update the PATH Variable**

In **System Variables**, select **Path**, then click **Edit** and add the following entries:

`C:\path\to\your\jdk-11.0.28`  
`C:\path\to\your\Programs\Python\Python310\`  
`C:\path\to\your\Programs\Python\Python310\Scripts\`  
`%HADOOP_HOME%\bin`  
`%JAVA_HOME%\bin     (must be at the top)`  
`%SPARK_HOME%\bin`

Make sure **%JAVA\_HOME%\\bin** appears above the others to avoid version conflicts.

4. ##  **Verify Installation**

After setting everything up, verify each tool:

### **Java**

`java -version`

### **Python**

`python --version`

### **Spark**

`pyspark`

### **Astronomer CLI**

`astro version`

If all commands run successfully, your environment is ready to start the program

