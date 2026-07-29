import database

def seed():
    print("Connecting to database and running schema initialization...")
    database.initialize()
    
    print("Clearing existing data...")
    try:
        database.execute("DELETE FROM Employee;")
        database.execute("DELETE FROM Department;")
    except Exception as e:
        print("Note: Could not clear tables. They might be empty. Continuing...")
        
    print("Inserting departments...")
    departments = [
        (1, 'Engineering', 'Seattle'),
        (2, 'Sales', 'New York'),
        (3, 'Marketing', 'San Francisco'),
        (4, 'Finance', 'Boston')
    ]
    for dept in departments:
        database.execute(
            "INSERT INTO Department (DepartmentID, DepartmentName, Location) VALUES (?, ?, ?);",
            dept
        )
        
    print("Inserting employees...")
    employees = [
        ('Alice', 'Smith', 1, 150000.00, 25000.00, '2019-03-01'),
        ('Bob', 'Johnson', 1, 100000.00, None, '2020-06-15'),
        ('Charlie', 'Brown', 2, 70000.00, 85000.00, '2018-01-10'),
        ('David', 'Lee', 2, 80000.00, 5000.00, '2021-08-20'),
        ('Emma', 'Davis', 3, 90000.00, None, '2022-11-05'),
        ('Frank', 'Wilson', 3, 85000.00, 10000.00, '2021-04-12'),
        ('Grace', 'Miller', 4, 120000.00, 4000.00, '2020-02-28')
    ]
    for emp in employees:
        database.execute(
            "INSERT INTO Employee (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate) VALUES (?, ?, ?, ?, ?, ?);",
            emp
        )
        
    print("Database successfully seeded in Python!")
    database.close()

if __name__ == '__main__':
    seed()
