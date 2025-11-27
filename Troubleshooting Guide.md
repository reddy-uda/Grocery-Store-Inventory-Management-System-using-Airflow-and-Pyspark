# **Troubleshooting Guide**

If you run into issues while working with the project, especially problems related to PostgreSQL or the Astronomer environment, this guide should help you sort them out quickly.

## **1\. When PostgreSQL Port 5432 Is Already in Use**

Sometimes Airflow or the pipeline can fail to connect because something else on your system is already using port 5432\. You can check that with the following commands.

### Check the PostgreSQL service

`Get-Service postgresql-x64-18`

If it shows that the service is running, stop it:

### Stop the service

`Stop-Service postgresql-x64-18`

## **2\. Find Out What Is Using Port 5432**

If PostgreSQL isn't the problem, then another program might be taking the port.

### See which process is using the port

`netstat -ano | findstr :5432`

This will show a PID (process ID).

### Identify the application

Replace 12345 with the PID you found:

`tasklist | findstr 12345`

### End the process

`taskkill /PID 12345 /F`

## **3\. Restart Astronomer**

If things still don’t work as expected, restarting the Astronomer setup usually helps.

`astro dev stop`

`astro dev kill`

`astro dev start`

## **4\. Reset the Entire Project Environment**

If the issue continues even after restarting, you may need to reset the full environment.

`astro dev stop`

`astro dev kill`

`astro dev reset`

`astro dev start`

This resets everything and builds the environment from scratch.

