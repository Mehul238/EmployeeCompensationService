-- Create Department Table if not exists
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Department' AND xtype='U')
BEGIN
    CREATE TABLE Department (
        DepartmentID INT PRIMARY KEY,
        DepartmentName VARCHAR(100) NOT NULL,
        Location VARCHAR(100) NULL
    );
END;

-- Create Employee Table if not exists
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Employee' AND xtype='U')
BEGIN
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
END;

-- Clear existing data for clean seed
DELETE FROM Employee;
DELETE FROM Department;

-- Seed Departments
INSERT INTO Department (DepartmentID, DepartmentName, Location) VALUES 
(1, 'Engineering', 'Seattle'),
(2, 'Sales', 'New York'),
(3, 'Marketing', 'San Francisco'),
(4, 'Finance', 'Boston');

-- Seed Employees
INSERT INTO Employee (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate) VALUES 
('Alice', 'Smith', 1, 150000.00, 25000.00, '2019-03-01'),
('Bob', 'Johnson', 1, 100000.00, NULL, '2020-06-15'),
('Charlie', 'Brown', 2, 70000.00, 85000.00, '2018-01-10'),
('David', 'Lee', 2, 80000.00, 5000.00, '2021-08-20'),
('Emma', 'Davis', 3, 90000.00, NULL, '2022-11-05'),
('Frank', 'Wilson', 3, 85000.00, 10000.00, '2021-04-12'),
('Grace', 'Miller', 4, 120000.00, 4000.00, '2020-02-28');
