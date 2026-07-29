# Employee Compensation Service - Serverless REST API

A modern, serverless REST API backend built as a set of HTTP-triggered Azure Functions (Python v2 Programming Model) backed by a serverless Azure SQL Database. The system is designed to manage employee records, apply dynamic business calculations, generate HR compensation reports, and integrate with Azure Logic Apps for automated workflow notifications.

---

## 🚀 Live API Endpoints
The application is deployed live in the Azure Cloud. You can access the API endpoints below:

### 📋 Employee Management (CRUD)
*   **Get All Employees (GET)**:
    `GET https://fn-comp-dhiraj-app.azurewebsites.net/api/employees`
    *Optional filter by department:* `GET https://fn-comp-dhiraj-app.azurewebsites.net/api/employees?departmentId=1`
*   **Get Single Employee (GET)**:
    `GET https://fn-comp-dhiraj-app.azurewebsites.net/api/employees/{id}`
*   **Create Employee (POST)**:
    `POST https://fn-comp-dhiraj-app.azurewebsites.net/api/employees`
*   **Update Employee (PUT)**:
    `PUT https://fn-comp-dhiraj-app.azurewebsites.net/api/employees/{id}`
*   **Delete Employee (DELETE)**:
    `DELETE https://fn-comp-dhiraj-app.azurewebsites.net/api/employees/{id}`

### 📊 HR Compensation Reports (GET)
*   **Total Bonus Paid**:
    `GET https://fn-comp-dhiraj-app.azurewebsites.net/api/reports/total-bonus`
*   **Employees with No Bonus**:
    `GET https://fn-comp-dhiraj-app.azurewebsites.net/api/reports/no-bonus`
*   **Bonus as Percentage of Salary**:
    `GET https://fn-comp-dhiraj-app.azurewebsites.net/api/reports/bonus-percentage`
*   **High-Bonus Departments**:
    `GET https://fn-comp-dhiraj-app.azurewebsites.net/api/reports/high-bonus-departments`
*   **Ranked Bonus Report**:
    `GET https://fn-comp-dhiraj-app.azurewebsites.net/api/reports/ranked-bonus`
*   **Salary Leader Analysis**:
    `GET https://fn-comp-dhiraj-app.azurewebsites.net/api/reports/salary-leader`

---

## 🛠️ Tech Stack & Key Concepts
*   **Runtime**: Python 3.11
*   **Framework**: Azure Functions Python v2 Programming Model (Modular structure utilizing `func.Blueprint()`)
*   **Databases**: SQLite (Local development/testing) & Azure SQL Database (Live production cloud)
*   **Libraries**: `pyodbc` (SQL database connector), `azure-functions` (Azure SDK)
*   **Integrations**: Automated POST alerts to Azure Logic Apps Webhook for HR notifications.

---

## 💻 Local Quickstart Guide

### 1. Prerequisite Installations
*   Ensure **Python 3.11** is installed.
*   Ensure **Node.js** (includes npm/npx) is installed.

### 2. Local Setup and Package Installation
Install dependencies in your local environment:
```powershell
python -m pip install -r requirements.txt
```

### 3. Initialize and Seed Local Database
Runs the SQL DDL/DML script against a local SQLite file:
```powershell
python src/seed.py
```

### 4. Run Local Functions Emulator Server
Launches the local server listening on port `7071`:
```powershell
npx func start
```
You can now test the API endpoints locally at `http://localhost:7071/api/employees`.

---

## ☁️ Azure Cloud Deployment Instructions

### 1. Authenticate with Azure CLI
Log in using your Azure credentials:
```powershell
az login --use-device-code
```

### 2. Register Web Resource Provider (One-time step)
Enables web resources inside a new subscription:
```powershell
az provider register --namespace Microsoft.Web
```
*(Verify status is `"Registered"` using `az provider show -n Microsoft.Web --query "registrationState"`)*

### 3. Create Serverless Azure Storage and Function App
Creates a Standard LRS storage account and a serverless Consumption Python app in Australia East:
```powershell
# Create Storage
az storage account create --name stcompdhiraj --resource-group rg-employee-compensation --location australiaeast --sku Standard_LRS --kind StorageV2

# Create Function App
az functionapp create --resource-group rg-employee-compensation --consumption-plan-location australiaeast --runtime python --runtime-version 3.11 --functions-version 4 --name fn-comp-dhiraj-app --storage-account stcompdhiraj --os-type Linux
```

### 4. Configure Application Environment Settings
Injects your SQL Server credentials securely:
```powershell
az functionapp config appsettings set --name fn-comp-dhiraj-app --resource-group rg-employee-compensation --settings SqlConnectionString="Driver={ODBC Driver 18 for SQL Server};Server=tcp:sqlserver-comp.database.windows.net,1433;Database=EmployeeCompDB;Uid=sqladmin;Pwd=YOUR_DB_PASSWORD;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

### 5. Deploy Code Live
Pushes code packages and compiles dependencies in the cloud:
```powershell
npx func azure functionapp publish fn-comp-dhiraj-app
```
