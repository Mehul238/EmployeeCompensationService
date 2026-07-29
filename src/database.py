import os
import sqlite3

connection_string = os.environ.get('SqlConnectionString', 'sqlite:employee_comp.db')
is_sqlite = connection_string.startswith('sqlite:')

db_connection = None

def get_db():
    global db_connection
    if is_sqlite:
        if db_connection is None:
            db_path = connection_string.replace('sqlite:', '')
            db_connection = sqlite3.connect(db_path, check_same_thread=False)
            db_connection.row_factory = sqlite3.Row
        return db_connection
    else:
        import pyodbc
        if db_connection is None:
            db_connection = pyodbc.connect(connection_string)
        return db_connection

def initialize():
    conn = get_db()
    cursor = conn.cursor()
    if is_sqlite:
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Department (
                DepartmentID INT PRIMARY KEY,
                DepartmentName VARCHAR(100) NOT NULL,
                Location VARCHAR(100) NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Employee (
                EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
                FirstName VARCHAR(50) NOT NULL,
                LastName VARCHAR(50) NOT NULL,
                DepartmentID INT,
                Salary DECIMAL(12,2) NOT NULL,
                Bonus DECIMAL(12,2) NULL,
                HireDate DATE,
                FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
            );
        """)
        conn.commit()
    else:
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Department' AND xtype='U')
            CREATE TABLE Department (
                DepartmentID INT PRIMARY KEY,
                DepartmentName VARCHAR(100) NOT NULL,
                Location VARCHAR(100) NULL
            );
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Employee' AND xtype='U')
            CREATE TABLE Employee (
                EmployeeID INT PRIMARY KEY IDENTITY(1,1),
                FirstName VARCHAR(50) NOT NULL,
                LastName VARCHAR(50) NOT NULL,
                DepartmentID INT,
                Salary DECIMAL(12,2) NOT NULL,
                Bonus DECIMAL(12,2) NULL,
                HireDate DATE,
                FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
            );
        """)
        conn.commit()

def query(sql, params=()):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    
    if is_sqlite:
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    else:
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

def execute(sql, params=()):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    
    last_id = None
    if is_sqlite:
        last_id = cursor.lastrowid
    else:
        if sql.strip().upper().startswith("INSERT"):
            try:
                cursor.execute("SELECT @@IDENTITY AS id")
                row = cursor.fetchone()
                if row:
                    last_id = int(row[0])
            except:
                pass
    return last_id

def close():
    global db_connection
    if db_connection:
        db_connection.close()
        db_connection = None
