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
