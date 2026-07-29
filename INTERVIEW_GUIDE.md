# 🎓 Interview Guide: Employee Compensation Service

This document provides an elevator pitch, architectural breakdown, key design highlights, and expected interview Q&As to help you confidently present this project during technical reviews or interviews.

---

## 1. The 2-Minute Elevator Pitch
> *"I have built a serverless, database-agnostic Employee Compensation REST API using the **Azure Functions Python v2 Programming Model** and an **Azure SQL Database**.*
>
> *The application handles full CRUD operations for managing employees, automatically calculates default 5% bonuses when omitted, generates aggregate HR reporting metrics, and integrates with **Azure Logic Apps** to trigger automated HR email alerts on updates. The entire system is built to be secure, cost-efficient, and modular, utilizing modern serverless architecture."*

---

## 2. Key Architecture & Design Decisions
These are the core engineering practices you should highlight to impress an interviewer:

### 2.1. Modular Design: Python V2 Blueprints
*   **Traditional V1 vs. Modern V2**: In older Azure Functions (V1), every endpoint required a separate directory with a `function.json` file. This led to project bloat.
*   **Our Approach**: We used the new **v2 Programming Model** with **Blueprints** (`func.Blueprint()`). This allows us to keep the code modular and clean by grouping related APIs together:
    *   [employees.py](file:///e:/LLM_AI_TESTING/new%20azure/EmployeeCompensationService/src/functions/employees.py) manages CRUD operations.
    *   [reporting.py](file:///e:/LLM_AI_TESTING/new%20azure/EmployeeCompensationService/src/functions/reporting.py) manages aggregate calculations.
    *   [function_app.py](file:///e:/LLM_AI_TESTING/new%20azure/EmployeeCompensationService/function_app.py) acts as the main entry point to register them.

### 2.2. Environment-Agnostic Database Layer
*   **The Problem**: QA environments, local developer machines, and cloud staging environments often use different databases. Re-writing code for each environment is error-prone.
*   **Our Solution**: In [database.py](file:///e:/LLM_AI_TESTING/new%20azure/EmployeeCompensationService/src/database.py), we built a database manager that automatically reads the system environment.
    *   If running locally, it detects local configurations and connects to a lightweight, file-based **SQLite** database (`employee_comp.db`).
    *   If running in the cloud, it connects to a secure, enterprise-ready **Azure SQL Database** using `pyodbc`.
    *   **The Result**: The exact same codebase runs offline locally and online in the cloud without modifying a single line of database code!

### 2.3. Decimal Division Fix (Database-Agnostic SQL)
*   In the Bonus Percentage calculation query ([reporting.py:L58](file:///e:/LLM_AI_TESTING/new%20azure/EmployeeCompensationService/src/functions/reporting.py#L58)):
    *   In SQLite, dividing two integers defaults to integer division (e.g. `25000 / 150000` is computed as `0`).
    *   We resolved this by explicitly casting the bonus column: `CAST(Bonus AS FLOAT)`. This ensures that correct decimal percentages (e.g. `16.67%`) are calculated consistently across SQLite and Microsoft SQL Server.

### 2.4. Decoupled Integrations: Logic Apps Webhook
*   When employee data changes, we trigger an external POST request to a webhook. We decamped this integration so that email notification processing does not block database commit requests, ensuring fast response times for clients.

### 2.5. Strict Security Controls
*   **No Hardcoded Passwords**: Your database password is never checked into Git or stored in code.
*   **Exclude Lists**: Used [.gitignore](file:///e:/LLM_AI_TESTING/new%20azure/EmployeeCompensationService/.gitignore) and [.funcignore](file:///e:/LLM_AI_TESTING/new%20azure/EmployeeCompensationService/.funcignore) to prevent local files, logs, and development environment variables from leaking to GitHub or bloating the cloud build package.

---

## 3. Core Database Schema & Structure
Explain the tables design in the SQL Database:
1.  **Department Table**: Holds department identities (`DepartmentID` primary key), names, and locations.
2.  **Employee Table**: Holds employee records (`EmployeeID` primary key), base salary, and bonus.
    *   It contains a foreign key constraint linking `DepartmentID` to the Department table, with `ON DELETE SET NULL` configurations to maintain structural integrity.

---

## 4. Expected Interview Questions & Answers (FAQ)

### Q1: Why did you choose Azure SQL Database (Serverless)?
> *"It is highly cost-effective for dev/test environments. With Auto-Pause enabled, the database shuts down and stops charging for compute capacity after 1 hour of idle time. The only charge is a few cents per month for disk space, which keeps cloud costs practically at $0."*

### Q2: How does your Python code read settings without hardcoding secrets?
> *"Azure Functions runtime automatically exposes any Application Setting (like SqlConnectionString) as standard OS environment variables. The code uses Python's `os.getenv('SqlConnectionString')` to read it at runtime, ensuring complete isolation of passwords from the repository source code."*

### Q3: What is the difference between `.gitignore` and `.funcignore`?
> * `.gitignore` blocks files from going to the public/private Git repository (e.g., local configuration settings).*
> * `.funcignore` blocks files from being zipped up and deployed to the live cloud servers (e.g., local databases or large virtual environments), keeping the upload package clean and preventing file lock errors during deployment.*
