from app.services.supabase import supabase
from app.services.utils import generate_id
import random
from datetime import datetime

# Sample employee data (will be replaced with database when integrated)
MOCK_EMPLOYEES = [
    {
        'id': 'emp_001',
        'name': 'John Smith',
        'email': 'john.smith@akc.com',
        'position': 'Project Manager',
        'department': 'Management',
        'payment_type': 'salary',
        'hourly_rate': 0.0,
        'annual_salary': 85000.0,
        'hours_per_week': 40,
        'is_active': True,
        'avatar_color': '#4e73df',
        'notes': '',
        'created_at': '2023-01-15'
    },
    {
        'id': 'emp_002',
        'name': 'Sarah Johnson',
        'email': 'sarah.johnson@akc.com',
        'position': 'Lead Engineer',
        'department': 'Engineering',
        'payment_type': 'salary',
        'hourly_rate': 0.0,
        'annual_salary': 95000.0,
        'hours_per_week': 40,
        'is_active': True,
        'avatar_color': '#1cc88a',
        'notes': '',
        'created_at': '2023-02-01'
    },
    {
        'id': 'emp_003',
        'name': 'Michael Davis',
        'email': 'michael.davis@akc.com',
        'position': 'Construction Worker',
        'department': 'Construction',
        'payment_type': 'hourly',
        'hourly_rate': 25.50,
        'annual_salary': 0.0,
        'hours_per_week': 35,
        'is_active': True,
        'avatar_color': '#f6c23e',
        'notes': '',
        'created_at': '2023-03-10'
    },
    {
        'id': 'emp_004',
        'name': 'Jessica Wilson',
        'email': 'jessica.wilson@akc.com',
        'position': 'Designer',
        'department': 'Design',
        'payment_type': 'hourly',
        'hourly_rate': 35.00,
        'annual_salary': 0.0,
        'hours_per_week': 30,
        'is_active': True,
        'avatar_color': '#e74a3b',
        'notes': '',
        'created_at': '2023-04-05'
    }
]

# List of avatar colors to randomly assign to new employees
AVATAR_COLORS = [
    '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#5a5c69', 
    '#6f42c1', '#fd7e14', '#20c997', '#6c757d'
]

def get_all_employees():
    """Get all employees from the database."""
    try:
        # TODO: Replace with actual database call
        employees = MOCK_EMPLOYEES
        return employees
    except Exception as e:
        print(f"Error getting employees: {e}")
        return []

def get_employee_by_id(employee_id):
    """Get a specific employee by ID."""
    try:
        # TODO: Replace with actual database call
        for employee in MOCK_EMPLOYEES:
            if employee['id'] == employee_id:
                return employee
        return None
    except Exception as e:
        print(f"Error getting employee {employee_id}: {e}")
        return None

def add_employee(employee_data):
    """Add a new employee to the database."""
    try:
        employee_id = generate_id(prefix='emp')
        avatar_color = random.choice(AVATAR_COLORS)
        
        # Set default values for the payment type
        if employee_data.get('payment_type') == 'hourly':
            hourly_rate = float(employee_data.get('hourly_rate', 0))
            annual_salary = 0.0
        else:  # salary
            hourly_rate = 0.0
            annual_salary = float(employee_data.get('annual_salary', 0))
        
        new_employee = {
            'id': employee_id,
            'name': employee_data.get('name', ''),
            'email': employee_data.get('email', ''),
            'position': employee_data.get('position', ''),
            'department': employee_data.get('department', 'Other'),
            'payment_type': employee_data.get('payment_type', 'hourly'),
            'hourly_rate': hourly_rate,
            'annual_salary': annual_salary,
            'hours_per_week': int(employee_data.get('hours_per_week', 40)),
            'is_active': bool(employee_data.get('is_active', True)),
            'avatar_color': avatar_color,
            'notes': employee_data.get('notes', ''),
            'created_at': datetime.now().strftime('%Y-%m-%d')
        }
        
        # TODO: Replace with actual database call
        MOCK_EMPLOYEES.append(new_employee)
        
        return new_employee
    except Exception as e:
        print(f"Error adding employee: {e}")
        return None

def edit_employee(employee_id, employee_data):
    """Update an existing employee in the database."""
    try:
        # TODO: Replace with actual database call
        for i, employee in enumerate(MOCK_EMPLOYEES):
            if employee['id'] == employee_id:
                # Set payment type values
                if employee_data.get('payment_type') == 'hourly':
                    hourly_rate = float(employee_data.get('hourly_rate', 0))
                    annual_salary = 0.0
                else:  # salary
                    hourly_rate = 0.0
                    annual_salary = float(employee_data.get('annual_salary', 0))
                
                # Update the employee
                MOCK_EMPLOYEES[i].update({
                    'name': employee_data.get('name', employee['name']),
                    'email': employee_data.get('email', employee['email']),
                    'position': employee_data.get('position', employee['position']),
                    'department': employee_data.get('department', employee['department']),
                    'payment_type': employee_data.get('payment_type', employee['payment_type']),
                    'hourly_rate': hourly_rate,
                    'annual_salary': annual_salary,
                    'hours_per_week': int(employee_data.get('hours_per_week', employee['hours_per_week'])),
                    'is_active': bool(employee_data.get('is_active', employee['is_active'])),
                    'notes': employee_data.get('notes', employee['notes'])
                })
                
                return MOCK_EMPLOYEES[i]
        
        return None
    except Exception as e:
        print(f"Error editing employee {employee_id}: {e}")
        return None

def delete_employee(employee_id):
    """Delete an employee from the database (or mark as inactive)."""
    try:
        # TODO: Replace with actual database call
        for i, employee in enumerate(MOCK_EMPLOYEES):
            if employee['id'] == employee_id:
                # Instead of deleting, mark as inactive
                MOCK_EMPLOYEES[i]['is_active'] = False
                return True
        
        return False
    except Exception as e:
        print(f"Error deleting employee {employee_id}: {e}")
        return False

def get_employee_hourly_cost(employee_id):
    """Calculate the hourly cost for an employee."""
    employee = get_employee_by_id(employee_id)
    if not employee:
        return 0.0
    
    if employee['payment_type'] == 'hourly':
        return float(employee['hourly_rate'])
    else:  # salary
        # Convert annual salary to hourly rate based on standard work hours
        weekly_hours = float(employee['hours_per_week'])
        if weekly_hours <= 0:
            weekly_hours = 40  # Default to 40 hours if not specified
        
        # Calculate hourly rate: annual salary / (52 weeks * hours per week)
        hourly_rate = float(employee['annual_salary']) / (52 * weekly_hours)
        return hourly_rate

def calculate_labor_cost(employee_id, hours_worked):
    """Calculate the labor cost for an employee for a given number of hours."""
    hourly_cost = get_employee_hourly_cost(employee_id)
    return hourly_cost * hours_worked

def get_department_statistics():
    """Get statistics about departments for visualization."""
    employees = get_all_employees()
    
    # Count employees by department
    departments = {}
    department_employees = {}
    
    for employee in employees:
        if employee['is_active']:  # Only count active employees
            dept = employee['department']
            if dept not in departments:
                departments[dept] = {
                    'count': 0,
                    'total_hourly_cost': 0.0
                }
                department_employees[dept] = []
            
            departments[dept]['count'] += 1
            department_employees[dept].append(employee)
    
    # Calculate average hourly cost by department
    for dept, data in departments.items():
        for employee in department_employees[dept]:
            hourly_cost = get_employee_hourly_cost(employee['id'])
            data['total_hourly_cost'] += hourly_cost
        
        if data['count'] > 0:
            data['avg_hourly_cost'] = data['total_hourly_cost'] / data['count']
        else:
            data['avg_hourly_cost'] = 0.0
    
    # Prepare data for charts
    department_labels = list(departments.keys())
    department_counts = [departments[dept]['count'] for dept in department_labels]
    department_costs = [departments[dept]['avg_hourly_cost'] for dept in department_labels]
    
    return {
        'department_labels': department_labels,
        'department_counts': department_counts,
        'department_costs': department_costs
    }

def get_employee_name_by_id(employee_id):
    """Get employee name by ID."""
    employee = get_employee_by_id(employee_id)
    if employee:
        return employee['name']
    return None 