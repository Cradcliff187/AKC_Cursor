from flask import (
    Blueprint, flash, g, redirect, render_template, request, 
    session, url_for, jsonify, current_app
)
from werkzeug.utils import secure_filename
from app.routes.auth import login_required
from app.services.user_context import (
    has_permission, render_appropriate_template,
    is_field_level_user, get_user_role
)
from app.services.projects import get_all_projects, get_project_by_id
from app.services.tasks import (
    get_project_tasks, get_user_tasks, update_task, 
    TASK_STATUSES, TASK_PRIORITIES, get_task
)
from app.services.time import (
    create_time_entry, get_user_time_entries,
    get_time_summary
)
from app.services.documents import save_uploaded_file
import os
from datetime import datetime, timedelta
import uuid
import json

bp = Blueprint('field', __name__, url_prefix='/field')

@bp.route('/')
@login_required
def dashboard():
    """Field worker dashboard - shows assigned tasks and recent time entries"""
    # Verify user has field-level permissions
    if not is_field_level_user():
        # Redirect admin users to admin dashboard
        return redirect(url_for('main.index'))
    
    # Get user's assigned tasks
    user_id = session.get('user_id', 'admin')
    tasks = get_user_tasks(user_id)
    
    # Get only active tasks (not completed or canceled)
    active_tasks = [t for t in tasks if t['status'] not in ['COMPLETED', 'CANCELED']]
    
    # Sort by priority and due date
    active_tasks.sort(key=lambda t: (
        0 if t['priority'] == 'high' else (1 if t['priority'] == 'medium' else 2),
        t.get('due_date', '9999-12-31')
    ))
    
    # Get user's recent time entries
    time_entries = get_user_time_entries(user_id)
    recent_entries = sorted(
        time_entries, 
        key=lambda e: e.get('date_worked', ''), 
        reverse=True
    )[:5]
    
    # Get time summary
    today = datetime.now().strftime('%Y-%m-%d')
    time_summary = get_time_summary(user_id, today)
    
    # Get projects the user is working on
    projects = get_all_projects()
    user_projects = []
    for task in tasks:
        for project in projects:
            if str(project['id']) == str(task['project_id']) and project not in user_projects:
                user_projects.append(project)
    
    return render_appropriate_template(
        'dashboard.html',
        active_tasks=active_tasks,
        recent_time_entries=recent_entries,
        time_summary=time_summary,
        projects=user_projects,
        statuses=TASK_STATUSES,
        priorities=TASK_PRIORITIES
    )

@bp.route('/tasks')
@login_required
def tasks():
    """Show user's assigned tasks with filtering options"""
    if not is_field_level_user():
        return redirect(url_for('tasks.list_tasks'))
    
    user_id = session.get('user_id', 'admin')
    
    # Get filter parameters
    status_filter = request.args.get('status', 'active')
    project_id = request.args.get('project_id')
    
    # Get all user tasks
    all_tasks = get_user_tasks(user_id)
    
    # Apply filters
    if status_filter == 'active':
        filtered_tasks = [t for t in all_tasks if t['status'] not in ['COMPLETED', 'CANCELED']]
    elif status_filter == 'completed':
        filtered_tasks = [t for t in all_tasks if t['status'] == 'COMPLETED']
    elif status_filter == 'all':
        filtered_tasks = all_tasks
    else:
        filtered_tasks = [t for t in all_tasks if t['status'] == status_filter]
    
    # Filter by project if specified
    if project_id:
        filtered_tasks = [t for t in filtered_tasks if str(t['project_id']) == str(project_id)]
    
    # Get projects for the filter dropdown
    projects = get_all_projects()
    
    # Sort tasks by priority and due date
    filtered_tasks.sort(key=lambda t: (
        0 if t['priority'] == 'high' else (1 if t['priority'] == 'medium' else 2),
        t.get('due_date', '9999-12-31')
    ))
    
    return render_appropriate_template(
        'tasks.html',
        tasks=filtered_tasks,
        projects=projects,
        current_project_id=project_id,
        status_filter=status_filter,
        statuses=TASK_STATUSES,
        priorities=TASK_PRIORITIES
    )

@bp.route('/task/<string:task_id>')
@login_required
def task_detail(task_id):
    """Show detailed task view optimized for mobile"""
    task = get_task(task_id)
    if not task:
        flash('Task not found')
        return redirect(url_for('field.tasks'))
    
    # Get project information
    project = get_project_by_id(task['project_id'])
    
    return render_appropriate_template(
        'task_detail.html',
        task=task,
        project=project,
        statuses=TASK_STATUSES,
        priorities=TASK_PRIORITIES
    )

@bp.route('/update_task_status', methods=['POST'])
@login_required
def update_task_status():
    """AJAX endpoint to update task status from mobile interface"""
    task_id = request.json.get('task_id')
    new_status = request.json.get('status')
    
    if not task_id or not new_status:
        return jsonify({'success': False, 'message': 'Missing task_id or status'})
    
    # Get the task to verify user has access to it
    task = get_task(task_id)
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'})
    
    # Verify user has permission to update this task
    user_id = session.get('user_id', 'admin')
    if task['assigned_to'] != user_id and not has_permission('assign_tasks'):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    # Update the task status
    result = update_task(task_id, {'status': new_status})
    
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to update task'})

@bp.route('/quick_log', methods=['GET', 'POST'])
@login_required
def quick_log_time():
    """Quick time entry form optimized for mobile"""
    if request.method == 'POST':
        # Get form data
        project_id = request.form.get('project_id')
        hours = request.form.get('hours', 1)
        description = request.form.get('description', '')
        
        if not project_id:
            flash('Project is required')
            return redirect(url_for('field.quick_log_time'))
        
        try:
            hours = float(hours)
        except ValueError:
            flash('Hours must be a number')
            return redirect(url_for('field.quick_log_time'))
        
        # Create time entry
        entry = create_time_entry({
            'project_id': project_id,
            'user_id': session.get('user_id', 'admin'),
            'hours': hours,
            'description': description,
            'date_worked': datetime.now().strftime('%Y-%m-%d'),
            'billable': True  # Default to billable
        })
        
        if entry:
            flash('Time logged successfully')
            return redirect(url_for('field.dashboard'))
        else:
            flash('Failed to log time')
    
    # Get projects for dropdown
    projects = get_all_projects()
    
    return render_appropriate_template(
        'quick_log.html',
        projects=projects,
        today=datetime.now().strftime('%Y-%m-%d')
    )

@bp.route('/timer')
@login_required
def timer():
    """Timer interface for tracking time in real-time"""
    # Get projects for dropdown
    projects = get_all_projects()
    
    return render_appropriate_template(
        'timer.html',
        projects=projects
    )

@bp.route('/save_timer', methods=['POST'])
@login_required
def save_timer():
    """Save timer data"""
    project_id = request.json.get('project_id')
    duration_minutes = request.json.get('duration_minutes')
    description = request.json.get('description', 'Time tracked with timer')
    
    if not project_id or not duration_minutes:
        return jsonify({'success': False, 'message': 'Missing required data'})
    
    try:
        # Convert duration to hours
        hours = float(duration_minutes) / 60.0
        hours = round(hours * 4) / 4  # Round to nearest 0.25
        
        # Create time entry
        entry = create_time_entry({
            'project_id': project_id,
            'user_id': session.get('user_id', 'admin'),
            'hours': hours,
            'description': description,
            'date_worked': datetime.now().strftime('%Y-%m-%d'),
            'billable': True
        })
        
        if entry:
            return jsonify({'success': True, 'entry': entry})
        else:
            return jsonify({'success': False, 'message': 'Failed to create time entry'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/upload_photo', methods=['GET', 'POST'])
@login_required
def upload_photo():
    """Photo upload interface optimized for mobile"""
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        description = request.form.get('description', '')
        photo = request.files.get('photo')
        
        if not project_id:
            flash('Project is required')
            return redirect(url_for('field.upload_photo'))
        
        if not photo:
            flash('No photo uploaded')
            return redirect(url_for('field.upload_photo'))
        
        # Save the uploaded file
        document = save_uploaded_file(photo, 'project', project_id, description)
        
        if document:
            flash('Photo uploaded successfully')
            return redirect(url_for('field.dashboard'))
        else:
            flash('Failed to upload photo')
    
    # Get projects for dropdown
    projects = get_all_projects()
    
    return render_appropriate_template(
        'upload_photo.html',
        projects=projects
    )

@bp.route('/materials')
@login_required
def materials():
    """View materials needed for projects"""
    # This would connect to a materials service in a full implementation
    # For now, let's create some sample data
    projects = get_all_projects()
    active_projects = [p for p in projects if p['status'] == 'IN_PROGRESS']
    
    materials_by_project = {}
    for project in active_projects:
        materials_by_project[project['id']] = [
            {
                'id': f"mat-{uuid.uuid4()}",
                'name': 'Lumber - 2x4x8',
                'quantity': 24,
                'unit': 'pieces',
                'status': 'needed'
            },
            {
                'id': f"mat-{uuid.uuid4()}",
                'name': 'Drywall - 4x8 sheets',
                'quantity': 12,
                'unit': 'sheets',
                'status': 'ordered'
            },
            {
                'id': f"mat-{uuid.uuid4()}",
                'name': 'Nails - 3 inch',
                'quantity': 5,
                'unit': 'lbs',
                'status': 'on_site'
            }
        ]
    
    return render_appropriate_template(
        'materials.html',
        projects=active_projects,
        materials_by_project=materials_by_project
    )

@bp.route('/request_material', methods=['POST'])
@login_required
def request_material():
    """Request materials for a project"""
    project_id = request.form.get('project_id')
    material_name = request.form.get('material_name')
    quantity = request.form.get('quantity', 1)
    unit = request.form.get('unit', 'pieces')
    
    if not project_id or not material_name:
        flash('Project and material name are required')
        return redirect(url_for('field.materials'))
    
    # This would connect to a materials service in a full implementation
    # For now, just show a success message
    flash(f'Material request submitted: {quantity} {unit} of {material_name}')
    return redirect(url_for('field.materials')) 