from app.services.supabase import supabase
from app.services.utils import generate_id
from app.services.employees import get_employee_by_id, calculate_labor_cost, get_employee_name_by_id
from app.services.projects import get_project_by_id, add_project_expense
from datetime import datetime

# Sample time entry data (will be replaced with database when integrated)
MOCK_TIME_ENTRIES = [
    {
        'id': 'time_001',
        'project_id': 'proj_001',
        'employee_id': 'emp_001',
        'date': '2023-05-15',
        'hours': 4.5,
        'billable': True,
        'description': 'Project planning and client consultation',
        'task_id': None,
        'created_at': '2023-05-15T14:30:00'
    },
    {
        'id': 'time_002',
        'project_id': 'proj_001',
        'employee_id': 'emp_002',
        'date': '2023-05-16',
        'hours': 6.0,
        'billable': True,
        'description': 'Initial design work for project requirements',
        'task_id': 'task_001',
        'created_at': '2023-05-16T18:00:00'
    },
    {
        'id': 'time_003',
        'project_id': 'proj_002',
        'employee_id': 'emp_003',
        'date': '2023-05-15',
        'hours': 8.0,
        'billable': True,
        'description': 'On-site construction work',
        'task_id': 'task_005',
        'created_at': '2023-05-15T17:30:00'
    }
]

def get_all_time_entries():
    """Get all time entries from the database."""
    try:
        # TODO: Replace with actual database call
        time_entries = MOCK_TIME_ENTRIES
        
        # Enhance time entries with employee and project names
        for entry in time_entries:
            entry['employee_name'] = get_employee_name_by_id(entry['employee_id'])
            project = get_project_by_id(entry['project_id'])
            entry['project_name'] = project['name'] if project else 'Unknown Project'
        
        return time_entries
    except Exception as e:
        print(f"Error getting time entries: {e}")
        return []

def get_time_entry_by_id(time_entry_id):
    """Get a specific time entry by ID."""
    try:
        # TODO: Replace with actual database call
        for entry in MOCK_TIME_ENTRIES:
            if entry['id'] == time_entry_id:
                return entry
        return None
    except Exception as e:
        print(f"Error getting time entry {time_entry_id}: {e}")
        return None

def get_time_entries_by_project(project_id):
    """Get all time entries for a specific project."""
    try:
        # TODO: Replace with actual database call
        entries = [entry for entry in MOCK_TIME_ENTRIES if entry['project_id'] == project_id]
        
        # Enhance time entries with employee names
        for entry in entries:
            entry['employee_name'] = get_employee_name_by_id(entry['employee_id'])
        
        return entries
    except Exception as e:
        print(f"Error getting time entries for project {project_id}: {e}")
        return []

def get_time_entries_by_employee(employee_id):
    """Get all time entries for a specific employee."""
    try:
        # TODO: Replace with actual database call
        entries = [entry for entry in MOCK_TIME_ENTRIES if entry['employee_id'] == employee_id]
        
        # Enhance time entries with project names
        for entry in entries:
            project = get_project_by_id(entry['project_id'])
            entry['project_name'] = project['name'] if project else 'Unknown Project'
        
        return entries
    except Exception as e:
        print(f"Error getting time entries for employee {employee_id}: {e}")
        return []

def add_time_entry(time_entry_data):
    """Add a new time entry to the database and create a cost expense for the project."""
    try:
        time_entry_id = generate_id(prefix='time')
        
        # Convert hours to float
        hours = float(time_entry_data.get('hours', 0))
        if hours <= 0:
            return None
        
        project_id = time_entry_data.get('project_id')
        employee_id = time_entry_data.get('employee_id')
        
        # Calculate labor cost for this time entry
        labor_cost = calculate_labor_cost(employee_id, hours)
        
        new_time_entry = {
            'id': time_entry_id,
            'project_id': project_id,
            'employee_id': employee_id,
            'date': time_entry_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'hours': hours,
            'billable': time_entry_data.get('billable', True),
            'description': time_entry_data.get('description', ''),
            'task_id': time_entry_data.get('task_id'),
            'created_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        }
        
        # TODO: Replace with actual database call
        MOCK_TIME_ENTRIES.append(new_time_entry)
        
        # Add a labor expense to the project
        employee = get_employee_by_id(employee_id)
        employee_name = employee['name'] if employee else 'Unknown Employee'
        
        expense_data = {
            'expense_type': 'labor',
            'amount': labor_cost,
            'date': new_time_entry['date'],
            'description': f"Labor: {employee_name} - {hours} hours - {new_time_entry['description']}",
            'added_by': 'system',
            'time_entry_id': time_entry_id
        }
        
        add_project_expense(project_id, expense_data)
        
        return new_time_entry
    except Exception as e:
        print(f"Error adding time entry: {e}")
        return None

def edit_time_entry(time_entry_id, time_entry_data):
    """Update an existing time entry in the database."""
    try:
        # TODO: Replace with actual database call
        for i, entry in enumerate(MOCK_TIME_ENTRIES):
            if entry['id'] == time_entry_id:
                # Calculate the difference in hours for expense adjustment
                old_hours = float(entry['hours'])
                new_hours = float(time_entry_data.get('hours', old_hours))
                
                project_id = entry['project_id']
                employee_id = entry['employee_id']
                
                # Update the time entry
                MOCK_TIME_ENTRIES[i].update({
                    'project_id': time_entry_data.get('project_id', entry['project_id']),
                    'employee_id': time_entry_data.get('employee_id', entry['employee_id']),
                    'date': time_entry_data.get('date', entry['date']),
                    'hours': new_hours,
                    'billable': time_entry_data.get('billable', entry['billable']),
                    'description': time_entry_data.get('description', entry['description']),
                    'task_id': time_entry_data.get('task_id', entry['task_id'])
                })
                
                # If hours or employee changed, update the labor expense
                if new_hours != old_hours or employee_id != time_entry_data.get('employee_id', employee_id):
                    # TODO: Create a function to update the existing labor expense
                    # For now, we'll just add a new adjustment expense
                    if new_hours != old_hours:
                        employee = get_employee_by_id(employee_id)
                        employee_name = employee['name'] if employee else 'Unknown Employee'
                        
                        # Calculate cost for the hours difference
                        hours_diff = new_hours - old_hours
                        cost_diff = calculate_labor_cost(employee_id, hours_diff)
                        
                        expense_data = {
                            'expense_type': 'labor',
                            'amount': cost_diff,
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'description': f"Labor adjustment: {employee_name} - {hours_diff} hours - {MOCK_TIME_ENTRIES[i]['description']}",
                            'added_by': 'system',
                            'time_entry_id': time_entry_id
                        }
                        
                        add_project_expense(project_id, expense_data)
                
                return MOCK_TIME_ENTRIES[i]
        
        return None
    except Exception as e:
        print(f"Error editing time entry {time_entry_id}: {e}")
        return None

def delete_time_entry(time_entry_id):
    """Delete a time entry from the database."""
    try:
        # TODO: Replace with actual database call
        for i, entry in enumerate(MOCK_TIME_ENTRIES):
            if entry['id'] == time_entry_id:
                # Create a negative expense to offset the original labor expense
                employee_id = entry['employee_id']
                hours = float(entry['hours'])
                project_id = entry['project_id']
                
                employee = get_employee_by_id(employee_id)
                employee_name = employee['name'] if employee else 'Unknown Employee'
                
                # Calculate negative cost for the deleted hours
                labor_cost = -calculate_labor_cost(employee_id, hours)
                
                expense_data = {
                    'expense_type': 'labor',
                    'amount': labor_cost,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'description': f"Removed labor: {employee_name} - {hours} hours - {entry['description']}",
                    'added_by': 'system',
                    'time_entry_id': time_entry_id
                }
                
                add_project_expense(project_id, expense_data)
                
                # Remove the time entry
                MOCK_TIME_ENTRIES.pop(i)
                return True
        
        return False
    except Exception as e:
        print(f"Error deleting time entry {time_entry_id}: {e}")
        return False

def get_project_time_summary(project_id):
    """Get a summary of time entries for a project."""
    time_entries = get_time_entries_by_project(project_id)
    
    total_hours = sum(float(entry['hours']) for entry in time_entries)
    billable_hours = sum(float(entry['hours']) for entry in time_entries if entry.get('billable', False))
    
    # Calculate total labor cost
    total_labor_cost = 0
    for entry in time_entries:
        employee_id = entry.get('employee_id')
        hours = float(entry.get('hours', 0))
        labor_cost = calculate_labor_cost(employee_id, hours)
        total_labor_cost += labor_cost
    
    # Get employee breakdown
    employees = {}
    for entry in time_entries:
        employee_id = entry.get('employee_id')
        employee_name = entry.get('employee_name') or get_employee_name_by_id(employee_id) or 'Unknown'
        
        if employee_id not in employees:
            employees[employee_id] = {
                'name': employee_name,
                'hours': 0,
                'cost': 0
            }
        
        hours = float(entry.get('hours', 0))
        employees[employee_id]['hours'] += hours
        employees[employee_id]['cost'] += calculate_labor_cost(employee_id, hours)
    
    return {
        'total_hours': total_hours,
        'billable_hours': billable_hours,
        'total_labor_cost': total_labor_cost,
        'employees': list(employees.values())
    } 