import azure.functions as func
from src.functions.employees import bp as employees_bp
from src.functions.reporting import bp as reporting_bp

# Initialize the global Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Register blueprints to load handlers programmatically
app.register_blueprint(employees_bp)
app.register_blueprint(reporting_bp)
