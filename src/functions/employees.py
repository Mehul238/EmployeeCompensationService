import azure.functions as func
import json
import logging
import os
import urllib.request
import src.database as db

bp = func.Blueprint()

def trigger_logic_app(first_name: str, last_name: str, action: str, salary: float, bonus: float):
    url = os.environ.get('LogicAppWebhookUrl')
    if not url:
        return
    
    payload = {
        "employeeName": f"{first_name} {last_name}",
        "action": action,
        "salary": float(salary) if salary is not None else 0.0,
        "bonus": float(bonus) if bonus is not None else 0.0
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            pass
    except Exception as e:
        logging.error(f"Failed to trigger Logic App: {str(e)}")


def format_employee(emp):
    if not emp:
        return None
    salary = float(emp['Salary'])
    bonus = float(emp['Bonus']) if emp['Bonus'] is not None else None
    return {
        'EmployeeID': emp['EmployeeID'],
        'FirstName': emp['FirstName'],
        'LastName': emp['LastName'],
        'DepartmentID': emp['DepartmentID'],
        'Salary': salary,
        'Bonus': bonus,
        # Part C Option: dynamic 5% default bonus
        'EffectiveBonus': bonus if bonus is not None else round(salary * 0.05, 2),
        'HasDefaultBonusApplied': bonus is None,
        'HireDate': str(emp['HireDate']) if emp['HireDate'] else None
    }

# 1. Create Employee (POST /api/employees)
@bp.route(route="employees", methods=["POST"])
def create_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON body"}),
                mimetype="application/json",
                status_code=400
            )
            
        first_name = req_body.get('FirstName')
        last_name = req_body.get('LastName')
        dept_id = req_body.get('DepartmentID')
        salary = req_body.get('Salary')
        bonus = req_body.get('Bonus')
        hire_date = req_body.get('HireDate')
        
        if not first_name or not last_name or dept_id is None or salary is None:
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields: FirstName, LastName, DepartmentID, Salary"}),
                mimetype="application/json",
                status_code=400
            )
            
        try:
            salary_num = float(salary)
            if salary_num < 0:
                raise ValueError()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Salary must be a non-negative decimal"}),
                mimetype="application/json",
                status_code=400
            )
            
        bonus_val = None
        if bonus is not None and bonus != "":
            try:
                bonus_num = float(bonus)
                if bonus_num < 0:
                    raise ValueError()
                bonus_val = bonus_num
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Bonus must be a non-negative decimal"}),
                    mimetype="application/json",
                    status_code=400
                )
                
        # Check if department exists
        dept_check = db.query("SELECT 1 FROM Department WHERE DepartmentID = ?;", (dept_id,))
        if not dept_check:
            return func.HttpResponse(
                json.dumps({"error": f"Department ID {dept_id} does not exist"}),
                mimetype="application/json",
                status_code=400
            )
            
        from datetime import date
        hire_date_val = hire_date if hire_date else str(date.today())
        
        # Insert
        sql = "INSERT INTO Employee (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate) VALUES (?, ?, ?, ?, ?, ?);"
        new_id = db.execute(sql, (first_name, last_name, dept_id, salary_num, bonus_val, hire_date_val))
        
        if not new_id:
            max_id_res = db.query("SELECT MAX(EmployeeID) as lastID FROM Employee;")
            new_id = max_id_res[0]['lastID']
            
        new_emp = db.query("SELECT * FROM Employee WHERE EmployeeID = ?;", (new_id,))
        
        # Trigger Logic App webhook if configured
        trigger_logic_app(first_name, last_name, "INSERT", salary_num, bonus_val)
        
        return func.HttpResponse(
            json.dumps(format_employee(new_emp[0])),
            mimetype="application/json",
            status_code=201
        )
    except Exception as e:
        logging.error(f"Error creating employee: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# 2. Get Single Employee (GET /api/employees/{id})
@bp.route(route="employees/{id}", methods=["GET"])
def get_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        emp_id_str = req.route_params.get('id')
        try:
            emp_id = int(emp_id_str)
        except (ValueError, TypeError):
            return func.HttpResponse(
                json.dumps({"error": "Invalid ID parameter"}),
                mimetype="application/json",
                status_code=400
            )
            
        rows = db.query("SELECT * FROM Employee WHERE EmployeeID = ?;", (emp_id,))
        if not rows:
            return func.HttpResponse(
                json.dumps({"error": f"Employee with ID {emp_id} not found"}),
                mimetype="application/json",
                status_code=404
            )
            
        return func.HttpResponse(
            json.dumps(format_employee(rows[0])),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error fetching employee: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# 3. Get Employees List / filter (GET /api/employees)
@bp.route(route="employees", methods=["GET"])
def get_employees_list(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        dept_id_param = req.params.get('departmentId')
        
        if dept_id_param:
            try:
                dept_id = int(dept_id_param)
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Query parameter departmentId must be an integer"}),
                    mimetype="application/json",
                    status_code=400
                )
            rows = db.query("SELECT * FROM Employee WHERE DepartmentID = ?;", (dept_id,))
        else:
            rows = db.query("SELECT * FROM Employee;")
            
        formatted = [format_employee(emp) for emp in rows]
        return func.HttpResponse(
            json.dumps(formatted),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error listing employees: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# 4. Update Employee (PUT /api/employees/{id})
@bp.route(route="employees/{id}", methods=["PUT"])
def update_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        emp_id_str = req.route_params.get('id')
        try:
            emp_id = int(emp_id_str)
        except (ValueError, TypeError):
            return func.HttpResponse(
                json.dumps({"error": "Invalid ID parameter"}),
                mimetype="application/json",
                status_code=400
            )
            
        rows = db.query("SELECT * FROM Employee WHERE EmployeeID = ?;", (emp_id,))
        if not rows:
            return func.HttpResponse(
                json.dumps({"error": f"Employee with ID {emp_id} not found"}),
                mimetype="application/json",
                status_code=404
            )
            
        current = rows[0]
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON body"}),
                mimetype="application/json",
                status_code=400
            )
            
        first_name = req_body.get('FirstName', current['FirstName'])
        last_name = req_body.get('LastName', current['LastName'])
        dept_id = req_body.get('DepartmentID', current['DepartmentID'])
        
        salary = req_body.get('Salary')
        salary_num = float(salary) if salary is not None else float(current['Salary'])
        if salary_num < 0:
            return func.HttpResponse(
                json.dumps({"error": "Salary must be a non-negative decimal"}),
                mimetype="application/json",
                status_code=400
            )
            
        bonus_val = current['Bonus']
        if 'Bonus' in req_body:
            bonus = req_body['Bonus']
            if bonus is None or bonus == "":
                bonus_val = None
            else:
                try:
                    bonus_num = float(bonus)
                    if bonus_num < 0:
                        raise ValueError()
                    bonus_val = bonus_num
                except ValueError:
                    return func.HttpResponse(
                        json.dumps({"error": "Bonus must be a non-negative decimal"}),
                        mimetype="application/json",
                        status_code=400
                    )
                    
        hire_date = req_body.get('HireDate', current['HireDate'])
        
        # Verify department if updated
        if dept_id != current['DepartmentID']:
            dept_check = db.query("SELECT 1 FROM Department WHERE DepartmentID = ?;", (dept_id,))
            if not dept_check:
                return func.HttpResponse(
                    json.dumps({"error": f"Department ID {dept_id} does not exist"}),
                    mimetype="application/json",
                    status_code=400
                )
                
        sql = """
            UPDATE Employee 
            SET FirstName = ?, LastName = ?, DepartmentID = ?, Salary = ?, Bonus = ?, HireDate = ?
            WHERE EmployeeID = ?;
        """
        db.execute(sql, (first_name, last_name, dept_id, salary_num, bonus_val, str(hire_date), emp_id))
        
        updated = db.query("SELECT * FROM Employee WHERE EmployeeID = ?;", (emp_id,))
        
        # Trigger Logic App webhook if configured
        trigger_logic_app(first_name, last_name, "UPDATE", salary_num, bonus_val)
        
        return func.HttpResponse(
            json.dumps(format_employee(updated[0])),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error updating employee: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# 5. Delete Employee (DELETE /api/employees/{id})
@bp.route(route="employees/{id}", methods=["DELETE"])
def delete_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db.initialize()
        emp_id_str = req.route_params.get('id')
        try:
            emp_id = int(emp_id_str)
        except (ValueError, TypeError):
            return func.HttpResponse(
                json.dumps({"error": "Invalid ID parameter"}),
                mimetype="application/json",
                status_code=400
            )
            
        rows = db.query("SELECT * FROM Employee WHERE EmployeeID = ?;", (emp_id,))
        if not rows:
            return func.HttpResponse(
                json.dumps({"error": f"Employee with ID {emp_id} not found"}),
                mimetype="application/json",
                status_code=404
            )
            
        db.execute("DELETE FROM Employee WHERE EmployeeID = ?;", (emp_id,))
        return func.HttpResponse(
            json.dumps({"message": f"Employee with ID {emp_id} deleted successfully"}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error deleting employee: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
