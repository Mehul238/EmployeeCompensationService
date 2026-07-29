# 📝 Interview Quick Reference Guide

This document contains a simplified, high-level overview of the technologies, calling flow, and files in this project. Use this for quick reference during your interview.

---

## 1. Tech Stack & Workflow (The 30-Second Summary)

### What Technologies We Used:
*   **Python**: Programming language for all backend logic.
*   **Azure Functions (Python V2)**: Serverless API framework.
*   **Azure SQL Database (Serverless)**: Cloud database for live data storage.
*   **SQLite**: File-based database for quick local testing.
*   **Git & GitHub**: Version control to track and host the code.

### How We Used Them:
1.  **Local Testing**: Wrote the code locally in Python and tested it using a local SQLite file (`employee_comp.db`).
2.  **Going Live**: Deployed the code to the Azure cloud using a single command: `npx func azure functionapp publish`.
3.  **Connecting to SQL**: In the cloud, the code reads the connection credentials from Environment Settings and uses the **`pyodbc`** driver to connect directly to the live **Azure SQL Database**.
4.  **Automatic Alerts**: Database updates trigger an HTTP POST webhook request to **Azure Logic Apps** to email notifications to the HR team.

---

## 2. Layer-by-Layer Request Flow

```text
[ Layer 1: Client ]        Postman, Browser, or Frontend
       │
       ▼ (Sends HTTP Request)
[ Layer 2: Routing ]       function_app.py (Blueprint routes)
       │
       ▼ (Passes request data)
[ Layer 3: Logic ]         Calculates default 5% bonus & calls webhook
       │
       ▼ (Runs database query helper)
[ Layer 4: Data Access ]   database.py (uses pyodbc / sqlite3)
       │
       ▼ (Executes SQL query)
[ Layer 5: Database ]      Azure SQL (Cloud) or SQLite (Local file)
```

*   **Layer 1: Client**: Sends the request (e.g. `GET /api/employees`).
*   **Layer 2: Routing**: Azure Functions maps the request to the correct Python function handler.
*   **Layer 3: Business Logic**: Code processes the request (calculates default 5% bonuses, handles reports).
*   **Layer 4: Data Access**: `database.py` manages connections and formats Python variables into SQL queries.
*   **Layer 5: Database**: The database executes the SQL queries and returns the rows.

---

## 3. Project File Catalog

### Configuration Files
*   **`function_app.py`**: The entry point. Imports and registers all API routes (Blueprints).
*   **`host.json`**: Configures global settings and logging for the Azure Functions host.
*   **`local.settings.json`**: Holds local paths and connection strings for offline testing.
*   **`requirements.txt`**: Specifies packages (like `pyodbc`) for Azure to install.
*   **`schema.sql`**: The database design script to create and populate tables.
*   **`.gitignore`**: Excludes local database files and secrets from GitHub.
*   **`.funcignore`**: Excludes development logs and databases from uploading to the cloud.

### Source Files (`src/`)
*   **`src/database.py`**: The database adapter. Automatically routes queries to SQLite (locally) or Azure SQL (cloud).
*   **`src/seed.py`**: Reads `schema.sql` to initialize your local SQLite database file (`employee_comp.db`).
*   **`src/functions/employees.py`**: Holds code for the 5 CRUD endpoints (and default 5% bonus calculations).
*   **`src/functions/reporting.py`**: Holds code for the 6 aggregate HR compensation reports.

---

## 4. In-Depth File-by-File Operations Guide

### 4.1. `function_app.py`
This is the core entry point of the serverless API. It initializes the Function App container using `func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)`. The `ANONYMOUS` setting opens public access without requiring access keys. It dynamically imports and attaches the modular Blueprints using `app.register_blueprint()`.

### 4.2. `src/database.py`
Manages connections and transactions dynamically:
*   **Auto-Routing**: Reads the `SqlConnectionString` environment variable. If it detects a SQL Server driver configuration (`Driver=`), it initializes connections using `pyodbc.connect()`. Otherwise, it falls back to a local SQLite database (`sqlite3.connect`).
*   **Formatting Utility**: Maps raw SQL tuple results to clean Python dictionaries dynamically by zipping database headers (`cursor.description`) with row values, matching the expected format for JSON API payloads.

### 4.3. `src/functions/employees.py`
Organizes the 5 CRUD endpoints:
*   **Create Employee (`POST /api/employees`)**: Validates JSON payloads, calculates a default 5% bonus if the `Bonus` field is absent or empty, sets `HasDefaultBonusApplied = True`, writes to the database, and fires an HTTP POST request to the Logic App webhook to send an alert.
*   **Get Employees List (`GET /api/employees`)**: Fetches all employees, with optional department filtering.
*   **Get Single Employee (`GET /api/employees/{id}`)**: Returns employee details by primary key, or throws a `404 Not Found`.
*   **Update Employee (`PUT /api/employees/{id}`)**: Modifies records and handles bonus recalculation rules.
*   **Delete Employee (`DELETE /api/employees/{id}`)**: Executes delete commands to purge records.

### 4.4. `src/functions/reporting.py`
Organizes the 6 aggregate reports:
*   **Total Bonus (`GET /api/reports/total-bonus`)**: Sums bonuses using `COALESCE(Bonus, 0)` so null fields count as `0.0`.
*   **No Bonus (`GET /api/reports/no-bonus`)**: Lists employees where `Bonus IS NULL`.
*   **Bonus Percentage (`GET /api/reports/bonus-percentage`)**: Casts `Bonus` to `FLOAT` to ensure decimal division works across both SQLite and SQL Server, returning percentage strings.
*   **High-Bonus Departments (`GET /api/reports/high-bonus-departments`)**: Groups and filters records using `HAVING SUM(e.Bonus) > AVG(e.Salary)`.
*   **Ranked Bonus (`GET /api/reports/ranked-bonus`)**: Sorts employees with a case statement to ensure those with no bonus are placed last.
*   **Salary Leader (`GET /api/reports/salary-leader`)**: Fetches the highest-salaried employee and compares them with the highest-compensated employee.

### 4.5. `schema.sql`
Defines the database architecture. Creates the `Department` table (Primary Key: `DepartmentID`) and the `Employee` table (Primary Key: `EmployeeID`). Configures the foreign key relationship with an `ON DELETE SET NULL` rule to preserve employee data if their department is removed. Seeds initial testing data.
