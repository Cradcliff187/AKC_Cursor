from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.services.time_entries import (
    get_all_time_entries, get_time_entry_by_id, get_time_entries_by_project,
    get_time_entries_by_employee, add_time_entry, edit_time_entry, delete_time_entry,
    get_project_time_summary
)
from app.services.projects import get_all_projects, get_project_by_id
from app.services.employees import (
    get_all_employees, get_employee_by_id, get_employee_hourly_cost,
    calculate_labor_cost, get_department_statistics
)
from app.services.utils import login_required
from datetime import datetime

bp = Blueprint('time_entries', __name__, url_prefix='/time-entries')

@bp.route('/')
@login_required
def time_entries_list():
    """View list of all time entries."""
    time_entries = get_all_time_entries()
    
    return render_template('time_entries_list.html', time_entries=time_entries)

@bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_time():
    """Log a new time entry."""
    if request.method == 'POST':
        # Get form data
        project_id = request.form.get('project_id')
        employee_id = request.form.get('employee_id')
        date = request.form.get('date')
        hours = request.form.get('hours')
        billable = 'billable' in request.form
        description = request.form.get('description')
        task_id = request.form.get('task_id') or None
        
        # Validate required fields
        if not project_id or not employee_id or not date or not hours or not description:
            flash('All required fields must be completed.', 'danger')
            return redirect(url_for('time_entries.log_time'))
        
        # Create time entry
        time_entry_data = {
            'project_id': project_id,
            'employee_id': employee_id,
            'date': date,
            'hours': hours,
            'billable': billable,
            'description': description,
            'task_id': task_id
        }
        
        result = add_time_entry(time_entry_data)
        if result:
            flash('Time entry logged successfully.', 'success')
            return redirect(url_for('time_entries.time_entries_list'))
        else:
            flash('Failed to log time entry. Please try again.', 'danger')
    
    # For GET request, show the form
    # Get the list of projects and employees for dropdowns
    projects = get_all_projects()
    employees = get_all_employees()
    
    # Get current user for pre-selecting employee
    current_user_id = session.get('user_id')
    
    # Get recent time entries for the sidebar
    time_entries = get_all_time_entries()
    recent_entries = time_entries[:5] if time_entries else []
    
    # Get employee costs for client-side calculation
    employee_costs = {}
    for employee in employees:
        employee_costs[employee['id']] = get_employee_hourly_cost(employee['id'])
    
    return render_template(
        'log_time.html',
        projects=projects,
        employees=employees,
        recent_entries=recent_entries,
        today=datetime.now().strftime('%Y-%m-%d'),
        current_user_id=current_user_id,
        employee_costs=employee_costs
    )

@bp.route('/edit/<time_entry_id>', methods=['GET', 'POST'])
@login_required
def edit_time_entry_route(time_entry_id):
    """Edit an existing time entry."""
    time_entry = get_time_entry_by_id(time_entry_id)
    if not time_entry:
        flash('Time entry not found.', 'danger')
        return redirect(url_for('time_entries.time_entries_list'))
    
    if request.method == 'POST':
        # Get form data
        project_id = request.form.get('project_id')
        employee_id = request.form.get('employee_id')
        date = request.form.get('date')
        hours = request.form.get('hours')
        billable = 'billable' in request.form
        description = request.form.get('description')
        task_id = request.form.get('task_id') or None
        
        # Validate required fields
        if not project_id or not employee_id or not date or not hours or not description:
            flash('All required fields must be completed.', 'danger')
            return redirect(url_for('time_entries.edit_time_entry_route', time_entry_id=time_entry_id))
        
        # Update time entry
        time_entry_data = {
            'project_id': project_id,
            'employee_id': employee_id,
            'date': date,
            'hours': hours,
            'billable': billable,
            'description': description,
            'task_id': task_id
        }
        
        result = edit_time_entry(time_entry_id, time_entry_data)
        if result:
            flash('Time entry updated successfully.', 'success')
            return redirect(url_for('time_entries.time_entries_list'))
        else:
            flash('Failed to update time entry. Please try again.', 'danger')
    
    # For GET request, show the form with existing data
    projects = get_all_projects()
    employees = get_all_employees()
    
    # Get current user for pre-selecting employee
    current_user_id = session.get('user_id')
    
    # Get employee costs for client-side calculation
    employee_costs = {}
    for employee in employees:
        employee_costs[employee['id']] = get_employee_hourly_cost(employee['id'])
    
    return render_template(
        'edit_time_entry.html',
        time_entry=time_entry,
        projects=projects,
        employees=employees,
        current_user_id=current_user_id,
        employee_costs=employee_costs
    )

@bp.route('/delete/<time_entry_id>', methods=['POST'])
@login_required
def delete_time_entry_route(time_entry_id):
    """Delete a time entry."""
    if delete_time_entry(time_entry_id):
        flash('Time entry deleted successfully.', 'success')
    else:
        flash('Failed to delete time entry. Please try again.', 'danger')
    
    return redirect(url_for('time_entries.time_entries_list'))

@bp.route('/project/<project_id>')
@login_required
def project_time_entries(project_id):
    """View time entries for a specific project."""
    project = get_project_by_id(project_id)
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('time_entries.time_entries_list'))
    
    time_entries = get_time_entries_by_project(project_id)
    time_summary = get_project_time_summary(project_id)
    
    return render_template(
        'project_time_entries.html',
        project=project,
        time_entries=time_entries,
        time_summary=time_summary
    )

@bp.route('/cost-report')
@login_required
def cost_report():
    """View labor cost report with filters and grouping options."""
    # Get filter parameters
    project_id = request.args.get('project_id')
    employee_id = request.args.get('employee_id')
    department = request.args.get('department')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    group_by = request.args.get('group_by', 'project')
    
    # Get data for filter dropdowns
    projects = get_all_projects()
    employees = get_all_employees()
    
    # Extract departments from employees
    departments = sorted(set(emp['department'] for emp in employees if emp['department']))
    
    # Get all time entries
    time_entries = get_all_time_entries()
    
    # Apply filters if provided
    filtered_entries = []
    for entry in time_entries:
        include = True
        
        if project_id and entry.get('project_id') != project_id:
            include = False
        
        if employee_id and entry.get('employee_id') != employee_id:
            include = False
            
        # Get employee to check department
        if department and include:
            employee = get_employee_by_id(entry.get('employee_id'))
            if not employee or employee.get('department') != department:
                include = False
                
        # Filter by date range
        if start_date and include:
            if entry.get('date') < start_date:
                include = False
                
        if end_date and include:
            if entry.get('date') > end_date:
                include = False
        
        if include:
            # Add employee department and cost calculation
            employee = get_employee_by_id(entry.get('employee_id'))
            entry['department'] = employee.get('department', 'Unknown') if employee else 'Unknown'
            entry['hourly_rate'] = get_employee_hourly_cost(entry.get('employee_id', ''))
            entry['cost'] = calculate_labor_cost(entry.get('employee_id', ''), float(entry.get('hours', 0)))
            filtered_entries.append(entry)
    
    # Calculate summary statistics
    total_hours = sum(float(entry.get('hours', 0)) for entry in filtered_entries)
    total_cost = sum(entry.get('cost', 0) for entry in filtered_entries)
    billable_hours = sum(float(entry.get('hours', 0)) for entry in filtered_entries if entry.get('billable', False))
    
    if total_hours > 0:
        billable_percentage = (billable_hours / total_hours) * 100
        avg_hourly_cost = total_cost / total_hours
    else:
        billable_percentage = 0
        avg_hourly_cost = 0
    
    # Count unique projects
    projects_count = len(set(entry.get('project_id') for entry in filtered_entries))
    
    # Calculate costs by project for chart
    project_costs = {}
    for entry in filtered_entries:
        project_id = entry.get('project_id')
        project = get_project_by_id(project_id)
        project_name = project.get('name', 'Unknown') if project else 'Unknown'
        
        if project_name not in project_costs:
            project_costs[project_name] = 0
        
        project_costs[project_name] += entry.get('cost', 0)
    
    # Take top 5 projects by cost
    top_projects = sorted(project_costs.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # If there are more than 5 projects, add an "Other" category
    if len(project_costs) > 5:
        other_cost = sum(cost for proj, cost in sorted(project_costs.items(), key=lambda x: x[1], reverse=True)[5:])
        if other_cost > 0:
            top_projects.append(("Other", other_cost))
    
    # Calculate costs by department for chart
    dept_costs = {}
    for entry in filtered_entries:
        department = entry.get('department', 'Unknown')
        
        if department not in dept_costs:
            dept_costs[department] = 0
        
        dept_costs[department] += entry.get('cost', 0)
    
    # Find top department by cost
    if dept_costs:
        top_dept_name, top_dept_cost = max(dept_costs.items(), key=lambda x: x[1])
        top_department = {
            'name': top_dept_name,
            'cost': top_dept_cost,
            'percentage': (top_dept_cost / total_cost * 100) if total_cost > 0 else 0
        }
    else:
        top_department = {
            'name': 'None',
            'cost': 0,
            'percentage': 0
        }
    
    # Prepare chart data
    project_cost_data = {
        'labels': [p[0] for p in top_projects],
        'values': [p[1] for p in top_projects]
    }
    
    dept_cost_data = {
        'labels': list(dept_costs.keys()),
        'values': list(dept_costs.values())
    }
    
    # Check if this is an AJAX request for regrouping
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'time_entries': filtered_entries,
            'total_hours': total_hours,
            'total_cost': total_cost
        })
    
    # Otherwise render the full template
    return render_template(
        'time_cost_report.html',
        time_entries=filtered_entries,
        projects=projects,
        employees=employees,
        departments=departments,
        total_hours=total_hours,
        total_cost=total_cost,
        billable_percentage=billable_percentage,
        avg_hourly_cost=avg_hourly_cost,
        projects_count=projects_count,
        top_department=top_department,
        project_cost_data=project_cost_data,
        dept_cost_data=dept_cost_data
    ) 