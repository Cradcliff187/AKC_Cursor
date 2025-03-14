from app.services.supabase import (
    get_table_data, insert_record, update_record, delete_record, execute_query
)
from app.models.project import Project
from app.services.utils import generate_project_id, generate_id
from datetime import datetime, timedelta
import json
from app.db import get_db

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

def get_all_projects(limit=50, offset=0, status=None, client_id=None):
    """Get all projects with optional filtering"""
    db = get_db()
    query = """
        SELECT p.*, c.name as client_name
        FROM projects p
        LEFT JOIN clients c ON p.client_id = c.id
    """
    params = []
    
    where_clauses = []
    if status:
        where_clauses.append("p.status = ?")
        params.append(status)
    
    if client_id:
        where_clauses.append("p.client_id = ?")
        params.append(client_id)
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY p.start_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    return db.execute(query, params).fetchall()

def get_project_by_id(project_id):
    """Get a project by ID"""
    db = get_db()
    return db.execute(
        """
        SELECT p.*, c.name as client_name
        FROM projects p
        LEFT JOIN clients c ON p.client_id = c.id
        WHERE p.id = ?
        """, 
        (project_id,)
    ).fetchone()

def get_projects_by_user(user_id):
    """Get all projects for a user"""
    project_data = get_table_data('projects', filters={'user_id': user_id})
    
    # Convert to Project objects
    projects = [Project.from_dict(p) for p in project_data]
    return projects

def create_project(project_data):
    """Create a new project"""
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO projects 
        (name, client_id, description, address, city, state, zip_code, 
         status, start_date, end_date, estimated_budget, created_by_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_data['name'],
            project_data.get('client_id'),
            project_data.get('description'),
            project_data.get('address'),
            project_data.get('city'),
            project_data.get('state'),
            project_data.get('zip_code'),
            project_data.get('status', 'active'),
            project_data.get('start_date'),
            project_data.get('end_date'),
            project_data.get('estimated_budget'),
            project_data.get('created_by_id')
        )
    )
    db.commit()
    return cursor.lastrowid

def update_project(project_id, project_data):
    """Update a project"""
    db = get_db()
    db.execute(
        """
        UPDATE projects 
        SET name = ?, client_id = ?, description = ?, address = ?, 
            city = ?, state = ?, zip_code = ?, status = ?, 
            start_date = ?, end_date = ?, estimated_budget = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            project_data['name'],
            project_data.get('client_id'),
            project_data.get('description'),
            project_data.get('address'),
            project_data.get('city'),
            project_data.get('state'),
            project_data.get('zip_code'),
            project_data.get('status'),
            project_data.get('start_date'),
            project_data.get('end_date'),
            project_data.get('estimated_budget'),
            project_id
        )
    )
    db.commit()
    return True

def delete_project(project_id):
    """Delete a project"""
    db = get_db()
    db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    db.commit()
    return True

def get_project_tasks(project_id):
    """Get all tasks for a project"""
    db = get_db()
    return db.execute(
        """
        SELECT t.*, u.username as assigned_to_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to_id = u.id
        WHERE t.project_id = ?
        ORDER BY t.due_date
        """,
        (project_id,)
    ).fetchall()

def get_project_documents(project_id):
    """Get all documents for a project"""
    db = get_db()
    return db.execute(
        "SELECT * FROM documents WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,)
    ).fetchall()

def get_project_invoices(project_id):
    """Get all invoices for a project"""
    db = get_db()
    return db.execute(
        "SELECT * FROM invoices WHERE project_id = ? ORDER BY issue_date DESC",
        (project_id,)
    ).fetchall()

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