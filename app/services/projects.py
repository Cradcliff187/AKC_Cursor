from app.services.supabase import (
    get_table_data, insert_record, update_record, delete_record, execute_query
)
from app.models.project import Project
from app.services.utils import generate_project_id, generate_id
from datetime import datetime, timedelta
import json

# Project status constants
PROJECT_STATUSES = ['Planning', 'In Progress', 'On Hold', 'Completed', 'Cancelled']

# Project type constants
PROJECT_TYPES = ['New Construction', 'Renovation', 'Remodel', 'Addition', 'Repair', 'Other']

# Valid status transitions
PROJECT_STATUS_TRANSITIONS = {
    'Planning': ['In Progress', 'On Hold', 'Cancelled'],
    'In Progress': ['On Hold', 'Completed', 'Cancelled'],
    'On Hold': ['In Progress', 'Cancelled'],
    'Completed': [],  # Can't transition out of completed
    'Cancelled': ['Planning']  # Can restart a cancelled project
}

def is_valid_status_transition(current_status, new_status):
    """Check if a status transition is valid"""
    return new_status in PROJECT_STATUS_TRANSITIONS.get(current_status, [])

def get_all_projects():
    """Get all projects from the database"""
    project_data = get_table_data('projects')
    
    # Convert to Project objects
    projects = [Project.from_dict(p) for p in project_data]
    return projects

def get_project_by_id(project_id):
    """Get a project by ID"""
    project_data = get_table_data('projects', filters={'id': project_id})
    
    if project_data and len(project_data) > 0:
        return Project.from_dict(project_data[0])
    return None

def get_projects_by_user(user_id):
    """Get all projects for a user"""
    project_data = get_table_data('projects', filters={'user_id': user_id})
    
    # Convert to Project objects
    projects = [Project.from_dict(p) for p in project_data]
    return projects

def create_project(project_data):
    """Create a new project"""
    # Create a Project object to validate the data
    project = Project.from_dict(project_data)
    
    # Insert the project into the database
    result = insert_record('projects', project.to_dict())
    
    if result:
        return Project.from_dict(result)
    return None

def update_project(project_id, project_data):
    """Update a project"""
    # First get the existing project
    existing_project = get_project_by_id(project_id)
    if not existing_project:
        return None
        
    # Check if status change is valid
    if 'status' in project_data and project_data['status'] != existing_project.status:
        if not is_valid_status_transition(existing_project.status, project_data['status']):
            raise ValueError(f"Invalid status transition from {existing_project.status} to {project_data['status']}")
    
    # Update the project
    result = update_record('projects', project_id, project_data)
    
    if result:
        return Project.from_dict(result)
    return None

def delete_project(project_id):
    """Delete a project"""
    return delete_record('projects', project_id)

def get_project_tasks(project_id):
    """Get all tasks for a project"""
    from app.services.tasks import get_tasks_by_project
    return get_tasks_by_project(project_id)

def get_project_financial_summary(project_id):
    """Get financial summary for a project"""
    project = get_project_by_id(project_id)
    if not project:
        return None
        
    # Get expenses from various sources
    # TODO: Implement actual queries for expenses, invoices, etc.
    
    summary = {
        'budget': project.budget,
        'budget_spent': project.budget_spent,
        'remaining_budget': project.budget - project.budget_spent if project.budget else 0,
        'over_budget': project.is_over_budget,
        'budget_percentage': project.budget_percentage,
        # Additional fields would be populated from actual data
        'expense_categories': {}
    }
    
    return summary

def add_project_expense(project_id, expense_data):
    """Add an expense to a project and update the budget spent"""
    # Insert the expense record
    result = insert_record('expenses', {**expense_data, 'project_id': project_id})
    
    if result:
        # Update the project's budget_spent
        project = get_project_by_id(project_id)
        if project:
            new_budget_spent = project.budget_spent + float(expense_data.get('amount', 0))
            update_project(project_id, {'budget_spent': new_budget_spent})
            
        return result
    return None

def get_project_timeline(project_id):
    """Get timeline events for a project"""
    project = get_project_by_id(project_id)
    if not project:
        return []
        
    # Get tasks sorted by due date
    tasks = get_project_tasks(project_id)
    tasks.sort(key=lambda t: t.due_date if t.due_date else datetime.max)
    
    # Create timeline events
    timeline = []
    
    # Add project start and end
    if project.start_date:
        timeline.append({
            'date': project.start_date,
            'type': 'project',
            'event': 'Project Start',
            'description': f"Project {project.name} started",
            'status': 'completed' if project.start_date < datetime.now() else 'upcoming'
        })
    
    if project.end_date:
        timeline.append({
            'date': project.end_date,
            'type': 'project',
            'event': 'Project End',
            'description': f"Project {project.name} scheduled completion",
            'status': 'completed' if project.is_completed else 'upcoming'
        })
    
    # Add task due dates
    for task in tasks:
        if task.due_date:
            timeline.append({
                'date': task.due_date,
                'type': 'task',
                'event': f"Task Due: {task.title}",
                'description': task.description,
                'status': 'completed' if task.is_completed else 'overdue' if task.is_overdue else 'upcoming',
                'task_id': task.id
            })
    
    # Sort by date
    timeline.sort(key=lambda e: e['date'])
    
    return timeline 