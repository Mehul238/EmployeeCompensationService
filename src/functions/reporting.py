import azure.functions as func
import json
import logging
import src.database as db

bp = func.Blueprint()

# 1. Total Bonus Paid (GET /api/reports/total-bonus)
@bp.route(route="reports/total-bonus", methods=["GET"])
def report_total_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        sql = "SELECT SUM(COALESCE(Bonus, 0)) as TotalBonusPaid FROM Employee;"
        rows = db.query(sql)
        total_bonus = float(rows[0]['TotalBonusPaid']) if rows and rows[0]['TotalBonusPaid'] is not None else 0.0
        return func.HttpResponse(
            json.dumps({"totalBonusPaid": total_bonus}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error computing total bonus: {str(e)}")
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

# 2. Employees with No Bonus (GET /api/reports/no-bonus)
@bp.route(route="reports/no-bonus", methods=["GET"])
def report_no_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        sql = "SELECT * FROM Employee WHERE Bonus IS NULL;"
        rows = db.query(sql)
        formatted = [{
            'EmployeeID': emp['EmployeeID'],
            'FirstName': emp['FirstName'],
            'LastName': emp['LastName'],
            'DepartmentID': emp['DepartmentID'],
            'Salary': float(emp['Salary']),
            'Bonus': None,
            'HireDate': str(emp['HireDate']) if emp['HireDate'] else None
        } for emp in rows]
        return func.HttpResponse(
            json.dumps(formatted),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error listing employees with no bonus: {str(e)}")
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

# 3. Bonus as Percentage of Salary (GET /api/reports/bonus-percentage)
@bp.route(route="reports/bonus-percentage", methods=["GET"])
def report_bonus_percentage(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        sql = """
            SELECT EmployeeID, FirstName, LastName, Salary, Bonus,
                   ROUND((CAST(Bonus AS FLOAT) / Salary) * 100, 2) as BonusPercentage
            FROM Employee 
            WHERE Bonus IS NOT NULL;
        """
        rows = db.query(sql)
        formatted = [{
            'EmployeeID': emp['EmployeeID'],
            'FirstName': emp['FirstName'],
            'LastName': emp['LastName'],
            'Salary': float(emp['Salary']),
            'Bonus': float(emp['Bonus']),
            'BonusPercentage': float(emp['BonusPercentage'])
        } for emp in rows]
        return func.HttpResponse(
            json.dumps(formatted),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error computing bonus percentages: {str(e)}")
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

# 4. High-Bonus Departments (GET /api/reports/high-bonus-departments)
@bp.route(route="reports/high-bonus-departments", methods=["GET"])
def report_high_bonus_departments(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        sql = """
            SELECT d.DepartmentID, d.DepartmentName, d.Location,
                   SUM(COALESCE(e.Bonus, 0)) as TotalBonusPaid,
                   AVG(e.Salary) as AverageSalary
            FROM Department d
            JOIN Employee e ON d.DepartmentID = e.DepartmentID
            GROUP BY d.DepartmentID, d.DepartmentName, d.Location
            HAVING SUM(COALESCE(e.Bonus, 0)) > AVG(e.Salary);
        """
        rows = db.query(sql)
        formatted = [{
            'DepartmentID': dept['DepartmentID'],
            'DepartmentName': dept['DepartmentName'],
            'Location': dept['Location'],
            'TotalBonusPaid': float(dept['TotalBonusPaid']),
            'AverageSalary': round(float(dept['AverageSalary']), 2)
        } for dept in rows]
        return func.HttpResponse(
            json.dumps(formatted),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error fetching high-bonus departments: {str(e)}")
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

# 5. Ranked Bonus (GET /api/reports/ranked-bonus)
@bp.route(route="reports/ranked-bonus", methods=["GET"])
def report_ranked_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        sql = """
            SELECT EmployeeID, FirstName, LastName, DepartmentID, Salary, Bonus 
            FROM Employee 
            ORDER BY CASE WHEN Bonus IS NULL THEN 1 ELSE 0 END ASC, Bonus DESC;
        """
        rows = db.query(sql)
        formatted = [{
            'Rank': index + 1,
            'EmployeeID': emp['EmployeeID'],
            'FirstName': emp['FirstName'],
            'LastName': emp['LastName'],
            'DepartmentID': emp['DepartmentID'],
            'Salary': float(emp['Salary']),
            'Bonus': float(emp['Bonus']) if emp['Bonus'] is not None else None
        } for index, emp in enumerate(rows)]
        return func.HttpResponse(
            json.dumps(formatted),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error generating ranked bonus report: {str(e)}")
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

# 6. Salary Leader Analysis (GET /api/reports/salary-leader)
@bp.route(route="reports/salary-leader", methods=["GET"])
def report_salary_leader(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        
        # A. Query employee with highest base salary
        salary_rows = db.query("SELECT EmployeeID, FirstName, LastName, Salary, Bonus FROM Employee ORDER BY Salary DESC;")
        if not salary_rows:
            return func.HttpResponse(json.dumps({"error": "No records found"}), mimetype="application/json", status_code=404)
            
        highest_salary_emp = salary_rows[0]
        highest_salary_val = float(highest_salary_emp['Salary'])
        highest_salary_bonus = float(highest_salary_emp['Bonus']) if highest_salary_emp['Bonus'] is not None else 0.0
        highest_salary_total_comp = highest_salary_val + highest_salary_bonus
        
        # B. Query employee with highest total compensation (Salary + Bonus)
        comp_rows = db.query("SELECT EmployeeID, FirstName, LastName, Salary, Bonus, (Salary + COALESCE(Bonus, 0)) as TotalComp FROM Employee ORDER BY (Salary + COALESCE(Bonus, 0)) DESC;")
        highest_comp_emp = comp_rows[0]
        highest_comp_val = float(highest_comp_emp['TotalComp'])
        
        is_same_person = highest_salary_emp['EmployeeID'] == highest_comp_emp['EmployeeID']
        
        return func.HttpResponse(
            json.dumps({
                "highestSalaryEmployee": {
                    "EmployeeID": highest_salary_emp['EmployeeID'],
                    "FirstName": highest_salary_emp['FirstName'],
                    "LastName": highest_salary_emp['LastName'],
                    "BaseSalary": highest_salary_val,
                    "Bonus": float(highest_salary_emp['Bonus']) if highest_salary_emp['Bonus'] is not None else None,
                    "TotalCompensation": highest_salary_total_comp
                },
                "highestCompensationEmployee": {
                    "EmployeeID": highest_comp_emp['EmployeeID'],
                    "FirstName": highest_comp_emp['FirstName'],
                    "LastName": highest_comp_emp['LastName'],
                    "BaseSalary": float(highest_comp_emp['Salary']),
                    "Bonus": float(highest_comp_emp['Bonus']) if highest_comp_emp['Bonus'] is not None else None,
                    "TotalCompensation": highest_comp_val
                },
                "isHighestSalaryAlsoHighestCompensation": "Yes" if is_same_person else "No"
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error running salary leader report: {str(e)}")
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)
