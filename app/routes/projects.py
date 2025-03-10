from flask import (
    Blueprint, flash, g, redirect, render_template, 
    request, session, url_for, jsonify
)
from app.routes.auth import login_required
from app.services.projects import (
    get_all_projects, get_project_by_id, create_project,
    update_project, delete_project, get_project_tasks,
    get_project_financial_summary, add_project_expense,
    get_project_timeline, PROJECT_STATUSES, PROJECT_STATUS_TRANSITIONS,
    PROJECT_TYPES, is_valid_status_transition
)
from app.services.clients import get_all_clients, get_client_by_id
from app.services.tasks import TASK_STATUSES
from app.services.user_context import can_edit_project
from datetime import datetime
from collections import defaultdict

bp = Blueprint('projects', __name__, url_prefix='/projects')

@bp.route('/')
@login_required
def list_projects():
    """Show all projects"""
    # Get filter parameters
    status_filter = request.args.get('status', '')
    client_filter = request.args.get('client', '')
    search_query = request.args.get('search', '')
    
    # Get all projects
    projects = get_all_projects()
    
    # Apply filters
    if status_filter:
        projects = [p for p in projects if p.get('status') == status_filter]
        
    if client_filter:
        projects = [p for p in projects if str(p.get('client_id')) == str(client_filter)]
        
    if search_query:
        search_query = search_query.lower()
        projects = [p for p in projects if 
                    search_query in p.get('name', '').lower() or 
                    search_query in p.get('description', '').lower() or
                    search_query in p.get('location', '').lower()]
    
    # Get clients for filter dropdown
    clients = get_all_clients()
    
    return render_template('project_list.html', 
                          projects=projects,
                          clients=clients,
                          statuses=PROJECT_STATUSES,
                          filters={
                              'status': status_filter,
                              'client': client_filter,
                              'search': search_query
                          })

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create_project():
    """Create a new project"""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        client_id = request.form.get('client_id')
        status = request.form.get('status', 'PENDING')
        project_type = request.form.get('project_type')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        budget = request.form.get('budget', 0)
        location = request.form.get('location', '')
        
        error = None
        
        if not name:
            error = 'Project name is required.'
        
        if error is not None:
            flash(error)
        else:
            # Prepare project data
            project_data = {
                'name': name,
                'description': description,
                'client_id': client_id,
                'status': status,
                'project_type': project_type,
                'start_date': start_date,
                'end_date': end_date,
                'budget': float(budget) if budget else 0.0,
                'budget_spent': 0.0,
                'location': location,
                'user_id': session.get('user_id'),
                'created_at': datetime.utcnow().isoformat(),
                'progress': 0  # Initial progress is 0
            }
            
            # Create the project
            project = create_project(project_data)
            
            if project:
                flash('Project created successfully!')
                return redirect(url_for('projects.view_project', project_id=project['id']))
            else:
                flash('Failed to create project.')
    
    # Get clients for dropdown
    clients = get_all_clients()
    
    return render_template('create_project.html',
                          clients=clients, 
                          statuses=PROJECT_STATUSES,
                          project_types=PROJECT_TYPES)

@bp.route('/<project_id>')
@login_required
def view_project(project_id):
    """View a single project's details"""
    project = get_project_by_id(project_id)
    
    if not project:
        flash('Project not found')
        return redirect(url_for('projects.list_projects'))
    
    # Get related client
    client = None
    if project.get('client_id'):
        client = get_client_by_id(project.get('client_id'))
        
    # Get financial summary
    financial_summary = get_project_financial_summary(project_id)
    
    # Get project tasks
    tasks = get_project_tasks(project_id)
    
    # Get project timeline
    timeline = get_project_timeline(project_id)
    
    # Get allowed status transitions for this project
    allowed_transitions = []
    if project.get('status') in PROJECT_STATUS_TRANSITIONS:
        allowed_transitions = PROJECT_STATUS_TRANSITIONS[project.get('status')]
    
    # Check if user can edit this project
    can_edit = can_edit_project(project_id)
    
    return render_template('project_detail.html', 
                          project=project,
                          client=client,
                          financial_summary=financial_summary,
                          tasks=tasks,
                          timeline=timeline,
                          statuses=PROJECT_STATUSES,
                          task_statuses=TASK_STATUSES,
                          project_types=PROJECT_TYPES,
                          allowed_transitions=allowed_transitions,
                          can_edit=can_edit)

@bp.route('/<project_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_project(project_id):
    """Edit a project"""
    project = get_project_by_id(project_id)
    
    if not project:
        flash('Project not found')
        return redirect(url_for('projects.list_projects'))
        
    # Check if user can edit this project
    if not can_edit_project(project_id):
        flash('You do not have permission to edit this project')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        client_id = request.form.get('client_id')
        status = request.form.get('status')
        project_type = request.form.get('project_type')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        budget = request.form.get('budget')
        location = request.form.get('location', '')
        
        error = None
        
        if not name:
            error = 'Project name is required.'
            
        if error is not None:
            flash(error)
        else:
            # Check if status transition is valid
            if status != project.get('status') and not is_valid_status_transition(project.get('status'), status):
                flash(f"Invalid status transition from {project.get('status')} to {status}")
                return redirect(url_for('projects.edit_project', project_id=project_id))
            
            # Prepare update data
            project_data = {
                'name': name,
                'description': description,
                'client_id': client_id,
                'status': status,
                'project_type': project_type,
                'start_date': start_date,
                'end_date': end_date,
                'location': location
            }
            
            # Update budget if changed
            if budget:
                project_data['budget'] = float(budget)
            
            # Automatically update progress based on status
            if status == 'PENDING':
                project_data['progress'] = 0
            elif status == 'APPROVED':
                project_data['progress'] = 25
            elif status == 'IN_PROGRESS':
                project_data['progress'] = 50
            elif status == 'COMPLETED':
                project_data['progress'] = 100
            elif status == 'CLOSED':
                project_data['progress'] = 100
            
            # Update project
            result = update_project(project_id, project_data)
            
            if result:
                flash('Project updated successfully!')
                return redirect(url_for('projects.view_project', project_id=project_id))
            else:
                flash('Failed to update project.')
    
    # Get clients for dropdown
    clients = get_all_clients()
    
    # Get allowed status transitions for this project
    allowed_transitions = []
    if project.get('status') in PROJECT_STATUS_TRANSITIONS:
        allowed_transitions = PROJECT_STATUS_TRANSITIONS[project.get('status')]
    
    return render_template('edit_project.html', 
                          project=project,
                          clients=clients,
                          statuses=PROJECT_STATUSES,
                          project_types=PROJECT_TYPES,
                          allowed_transitions=allowed_transitions)

@bp.route('/<project_id>/delete', methods=('POST',))
@login_required
def delete_project(project_id):
    """Delete a project"""
    project = get_project_by_id(project_id)
    
    if not project:
        flash('Project not found')
        return redirect(url_for('projects.list_projects'))
    
    # Check if user can edit this project
    if not can_edit_project(project_id):
        flash('You do not have permission to delete this project')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    # Attempt to delete
    if delete_project(project_id):
        flash('Project deleted successfully!')
    else:
        flash('Failed to delete project.')
        
    return redirect(url_for('projects.list_projects'))

@bp.route('/<project_id>/add-expense', methods=('POST',))
@login_required
def add_expense(project_id):
    """Add an expense to a project"""
    project = get_project_by_id(project_id)
    
    if not project:
        flash('Project not found')
        return redirect(url_for('projects.list_projects'))
    
    # Check if user can edit this project
    if not can_edit_project(project_id):
        flash('You do not have permission to add expenses to this project')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    if request.method == 'POST':
        expense_type = request.form.get('expense_type', 'other')
        amount = request.form.get('amount', 0)
        description = request.form.get('description', '')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if not amount or float(amount) <= 0:
            flash('Amount must be greater than zero')
            return redirect(url_for('projects.view_project', project_id=project_id))
        
        # Prepare expense data
        expense_data = {
            'type': expense_type,
            'amount': float(amount),
            'description': description,
            'date': date,
            'added_by': session.get('user_id')
        }
        
        # Add expense
        if add_project_expense(project_id, expense_data):
            flash('Expense added successfully!')
        else:
            flash('Failed to add expense.')
            
    return redirect(url_for('projects.view_project', project_id=project_id))

@bp.route('/<project_id>/status/<new_status>', methods=('POST',))
@login_required
def update_status(project_id, new_status):
    """Update project status"""
    project = get_project_by_id(project_id)
    
    if not project:
        flash('Project not found')
        return redirect(url_for('projects.list_projects'))
    
    # Check if user can edit this project
    if not can_edit_project(project_id):
        flash('You do not have permission to update this project status')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    # Check if transition is valid
    if not is_valid_status_transition(project['status'], new_status):
        flash(f"Invalid status transition from {project['status']} to {new_status}")
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    # Set progress based on new status
    progress = 0
    if new_status == 'PENDING':
        progress = 0
    elif new_status == 'APPROVED':
        progress = 25
    elif new_status == 'IN_PROGRESS':
        progress = 50
    elif new_status == 'COMPLETED':
        progress = 100
    elif new_status == 'CLOSED':
        progress = 100
    
    # Update project
    update_data = {
        'status': new_status,
        'progress': progress,
        'updated_at': datetime.utcnow().isoformat()
    }
    
    result = update_project(project_id, update_data)
    
    if result:
        flash(f'Project status updated to {PROJECT_STATUSES[new_status]["display"]}')
    else:
        flash('Failed to update project status')
        
    return redirect(url_for('projects.view_project', project_id=project_id))

@bp.route('/<project_id>/timeline')
@login_required
def project_timeline(project_id):
    """View project timeline"""
    project = get_project_by_id(project_id)
    
    if not project:
        flash('Project not found')
        return redirect(url_for('projects.list_projects'))
    
    # Get project timeline
    timeline = get_project_timeline(project_id)
    
    # Get client
    client = None
    if project.get('client_id'):
        client = get_client_by_id(project.get('client_id'))
    
    return render_template('project_timeline.html',
                          project=project,
                          client=client,
                          timeline=timeline)

@bp.route('/api/projects')
@login_required
def api_projects():
    """API endpoint for projects"""
    projects = get_all_projects()
    return jsonify(projects)

@bp.route('/api/project/<project_id>')
@login_required
def api_project(project_id):
    """API endpoint for a single project"""
    project = get_project_by_id(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify(project)

@bp.route('/<project_id>/expenses')
@login_required
def project_expenses(project_id):
    """View all expenses for a project with filtering, analytics, and export capabilities."""
    project = get_project_by_id(project_id)
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('projects.list_projects'))

    # Get financial summary for the project
    financial_summary = get_project_financial_summary(project_id)
    
    # Get client information if available
    client = None
    if project.get('client_id'):
        client = get_client_by_id(project.get('client_id'))
    
    # Get all expenses for the project
    expenses = []
    if 'expenses' in project:
        expenses = project['expenses']
    
    # Prepare chart data
    expense_categories = ['Labor', 'Material', 'Subcontractor', 'Other']
    expense_category_amounts = [0, 0, 0, 0]
    
    # Group expenses by month for trend chart
    monthly_expenses = defaultdict(float)
    today = datetime.today().strftime('%Y-%m-%d')
    
    for expense in expenses:
        # For category chart
        if expense['expense_type'].lower() == 'labor':
            expense_category_amounts[0] += float(expense['amount'])
        elif expense['expense_type'].lower() == 'material':
            expense_category_amounts[1] += float(expense['amount'])
        elif expense['expense_type'].lower() == 'subcontractor':
            expense_category_amounts[2] += float(expense['amount'])
        else:
            expense_category_amounts[3] += float(expense['amount'])
        
        # For trend chart - format date to YYYY-MM
        try:
            expense_date = datetime.strptime(expense['date'], '%Y-%m-%d')
            month_key = expense_date.strftime('%Y-%m')
            monthly_expenses[month_key] += float(expense['amount'])
        except (ValueError, KeyError):
            # Handle invalid dates gracefully
            pass
    
    # Sort months for the trend chart
    sorted_months = sorted(monthly_expenses.keys())
    expense_months = [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in sorted_months]
    expense_monthly_amounts = [monthly_expenses[month] for month in sorted_months]
    
    # Check if user can edit the project
    can_edit = True  # In a real app, check permissions
    
    return render_template(
        'project_expenses.html',
        project=project,
        client=client,
        financial_summary=financial_summary,
        expenses=expenses,
        expense_categories=expense_categories,
        expense_category_amounts=expense_category_amounts,
        expense_months=expense_months,
        expense_monthly_amounts=expense_monthly_amounts,
        today=today,
        can_edit=can_edit,
        statuses=PROJECT_STATUSES
    )

@bp.route('/<project_id>/edit-expense', methods=('POST',))
@login_required
def edit_expense(project_id):
    """Edit an existing expense for a project."""
    if request.method == 'POST':
        expense_id = request.form.get('expense_id')
        expense_type = request.form.get('expense_type')
        amount = request.form.get('amount')
        date = request.form.get('date')
        description = request.form.get('description')
        
        if not expense_id or not expense_type or not amount or not date:
            flash('All required fields must be filled out.', 'danger')
            return redirect(url_for('projects.project_expenses', project_id=project_id))
        
        # Update the expense in the database
        project = get_project_by_id(project_id)
        if not project or 'expenses' not in project:
            flash('Project not found or has no expenses.', 'danger')
            return redirect(url_for('projects.list_projects'))
        
        # Find the expense to update
        updated = False
        for i, expense in enumerate(project['expenses']):
            if expense.get('id') == expense_id:
                # Calculate the difference in amount
                old_amount = float(expense['amount'])
                new_amount = float(amount)
                
                # Update the expense
                project['expenses'][i] = {
                    'id': expense_id,
                    'expense_type': expense_type,
                    'amount': new_amount,
                    'date': date,
                    'description': description,
                    'added_by': expense.get('added_by'),
                    'timestamp': expense.get('timestamp')
                }
                
                # Update the project's budget_spent
                if 'budget_spent' in project:
                    project['budget_spent'] = float(project['budget_spent']) - old_amount + new_amount
                
                updated = True
                break
        
        if updated:
            # Save the updated project
            update_project(project_id, project)
            flash('Expense updated successfully.', 'success')
        else:
            flash('Expense not found.', 'danger')
            
        return redirect(url_for('projects.project_expenses', project_id=project_id))
    
    return redirect(url_for('projects.view_project', project_id=project_id))

@bp.route('/<project_id>/delete-expense', methods=('POST',))
@login_required
def delete_expense(project_id):
    """Delete an expense from a project."""
    if request.method == 'POST':
        expense_id = request.form.get('expense_id')
        
        if not expense_id:
            flash('Expense ID is required.', 'danger')
            return redirect(url_for('projects.project_expenses', project_id=project_id))
        
        # Get the project and remove the expense
        project = get_project_by_id(project_id)
        if not project or 'expenses' not in project:
            flash('Project not found or has no expenses.', 'danger')
            return redirect(url_for('projects.list_projects'))
        
        # Find and remove the expense
        removed = False
        for i, expense in enumerate(project['expenses']):
            if expense.get('id') == expense_id:
                # Subtract the expense amount from budget_spent
                if 'budget_spent' in project:
                    project['budget_spent'] = float(project['budget_spent']) - float(expense['amount'])
                
                # Remove the expense
                project['expenses'].pop(i)
                removed = True
                break
        
        if removed:
            # Save the updated project
            update_project(project_id, project)
            flash('Expense deleted successfully.', 'success')
        else:
            flash('Expense not found.', 'danger')
            
        return redirect(url_for('projects.project_expenses', project_id=project_id))
    
    return redirect(url_for('projects.view_project', project_id=project_id)) 