from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.employees import (
    get_all_employees, get_employee_by_id, add_employee, 
    edit_employee, delete_employee, get_department_statistics
)
from app.services.utils import login_required

bp = Blueprint('employees', __name__, url_prefix='/employees')

@bp.route('/')
@login_required
def employee_list():
    """View list of all employees."""
    employees = get_all_employees()
    
    # Get department statistics for charts
    statistics = get_department_statistics()
    
    return render_template(
        'employee_management.html', 
        employees=employees,
        department_labels=statistics['department_labels'],
        department_counts=statistics['department_counts'],
        department_costs=statistics['department_costs']
    )

@bp.route('/add', methods=['POST'])
@login_required
def add_employee_route():
    """Add a new employee."""
    if request.method == 'POST':
        employee_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'position': request.form.get('position'),
            'department': request.form.get('department'),
            'payment_type': request.form.get('payment_type'),
            'hourly_rate': request.form.get('hourly_rate', 0),
            'annual_salary': request.form.get('annual_salary', 0),
            'hours_per_week': request.form.get('hours_per_week', 40),
            'is_active': 'is_active' in request.form,
            'notes': request.form.get('notes', '')
        }
        
        result = add_employee(employee_data)
        if result:
            flash(f"Employee {result['name']} added successfully.", 'success')
        else:
            flash("Failed to add employee. Please try again.", 'danger')
    
    return redirect(url_for('employees.employee_list'))

@bp.route('/edit', methods=['POST'])
@login_required
def edit_employee_route():
    """Edit an existing employee."""
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        
        employee_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'position': request.form.get('position'),
            'department': request.form.get('department'),
            'payment_type': request.form.get('payment_type'),
            'hourly_rate': request.form.get('hourly_rate', 0),
            'annual_salary': request.form.get('annual_salary', 0),
            'hours_per_week': request.form.get('hours_per_week', 40),
            'is_active': 'is_active' in request.form,
            'notes': request.form.get('notes', '')
        }
        
        result = edit_employee(employee_id, employee_data)
        if result:
            flash(f"Employee {result['name']} updated successfully.", 'success')
        else:
            flash("Failed to update employee. Please try again.", 'danger')
    
    return redirect(url_for('employees.employee_list'))

@bp.route('/delete', methods=['POST'])
@login_required
def delete_employee_route():
    """Delete an employee (mark as inactive)."""
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        
        if delete_employee(employee_id):
            flash("Employee deactivated successfully.", 'success')
        else:
            flash("Failed to deactivate employee. Please try again.", 'danger')
    
    return redirect(url_for('employees.employee_list')) 