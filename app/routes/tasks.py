from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, jsonify
)
from app.routes.auth import login_required
from app.services.tasks import (
    get_all_tasks, get_task, get_project_tasks, get_user_tasks,
    create_task, update_task, delete_task, get_task_stats,
    get_priority_display, get_status_display, TASK_PRIORITIES, TASK_STATUSES,
    TASK_STATUS_MAPPING, TASK_PRIORITY_MAPPING, get_task_timeline,
    is_valid_status_transition, get_task_dependencies, standardize_task_status,
    standardize_task_priority
)
from app.services.projects import get_all_projects, get_project_by_id
from app.services.users import get_all_users
from datetime import datetime

bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@bp.route('/')
@login_required
def list_tasks():
    """Show all tasks"""
    try:
        # Get filter parameters
        status_filter = request.args.get('status', '')
        priority_filter = request.args.get('priority', '')
        project_filter = request.args.get('project_id', '')
        
        tasks = get_all_tasks()
        projects = get_all_projects()
        
        # Apply filters
        if status_filter:
            # Map legacy status to standardized format if needed
            if status_filter in TASK_STATUS_MAPPING:
                status_filter = TASK_STATUS_MAPPING[status_filter]
            status_filter = status_filter.upper()
            tasks = [t for t in tasks if t.get('status') == status_filter]
            
        if priority_filter:
            # Map legacy priority to standardized format if needed
            if priority_filter in TASK_PRIORITY_MAPPING:
                priority_filter = TASK_PRIORITY_MAPPING[priority_filter]
            priority_filter = priority_filter.upper()
            tasks = [t for t in tasks if t.get('priority') == priority_filter]
            
        if project_filter:
            tasks = [t for t in tasks if t.get('project_id') == project_filter]
        
        # Get statistics for filtered tasks
        stats = get_task_stats()
        
        return render_template('tasks/index.html', 
                              tasks=tasks, 
                              projects=projects,
                              stats=stats,
                              priorities=TASK_PRIORITIES,
                              statuses=TASK_STATUSES,
                              filters={
                                  'status': status_filter,
                                  'priority': priority_filter,
                                  'project_id': project_filter
                              })
    except Exception as e:
        flash(f'Error loading tasks: {str(e)}')
        return render_template('tasks/index.html', 
                              tasks=[], 
                              projects=[],
                              stats={},
                              priorities=TASK_PRIORITIES,
                              statuses=TASK_STATUSES,
                              filters={})

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create_task_route():
    """Create a new task"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        project_id = request.form['project_id']
        assigned_to = request.form.get('assigned_to', session.get('user_id', 'admin'))
        status = request.form.get('status', 'PENDING')
        priority = request.form.get('priority', 'MEDIUM')
        due_date = request.form.get('due_date', '')
        estimated_hours = request.form.get('estimated_hours', 0)
        
        error = None
        
        if not title:
            error = 'Title is required.'
        if not project_id:
            error = 'Project is required.'
            
        if error is not None:
            flash(error)
        else:
            try:
                # Standardize status and priority
                if status in TASK_STATUS_MAPPING:
                    status = TASK_STATUS_MAPPING[status]
                status = status.upper()
                
                if priority in TASK_PRIORITY_MAPPING:
                    priority = TASK_PRIORITY_MAPPING[priority]
                priority = priority.upper()
                
                task_data = {
                    'title': title,
                    'description': description,
                    'project_id': project_id,
                    'assigned_to': assigned_to,
                    'status': status,
                    'priority': priority,
                    'due_date': due_date,
                    'estimated_hours': float(estimated_hours) if estimated_hours else 0,
                    'actual_hours': 0,
                    'created_by': session.get('user_id', 'admin')
                }
                
                result = create_task(task_data)
                
                if result:
                    flash('Task created successfully!')
                    return redirect(url_for('tasks.list_tasks'))
                else:
                    flash('Error creating task')
            except Exception as e:
                flash(f'Error creating task: {str(e)}')
    
    # Get projects and users for dropdowns
    projects = get_all_projects()
    users = get_all_users()  # This function needs to be implemented
    
    return render_template('tasks/create.html', 
                          projects=projects,
                          users=users,
                          priorities=TASK_PRIORITIES,
                          statuses=TASK_STATUSES,
                          default_status='PENDING',
                          default_priority='MEDIUM')

@bp.route('/<task_id>')
@login_required
def view_task(task_id):
    """View a single task"""
    task = get_task(task_id)
    
    if task is None:
        flash('Task not found')
        return redirect(url_for('tasks.list_tasks'))
    
    # Get the project for this task
    project = get_project_by_id(task['project_id']) if task.get('project_id') else None
    
    # Get dependent tasks
    dependencies = get_task_dependencies(task_id)
    
    return render_template('tasks/detail.html', 
                          task=task, 
                          project=project,
                          dependencies=dependencies,
                          priority_info=get_priority_display(task['priority']),
                          status_info=get_status_display(task['status']),
                          allowed_transitions=TASK_STATUS_TRANSITIONS.get(task['status'], []))

@bp.route('/<task_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_task(task_id):
    """Edit a task"""
    task = get_task(task_id)
    
    if task is None:
        flash('Task not found')
        return redirect(url_for('tasks.list_tasks'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        project_id = request.form['project_id']
        assigned_to = request.form.get('assigned_to', task['assigned_to'])
        status = request.form.get('status', task['status'])
        priority = request.form.get('priority', task['priority'])
        due_date = request.form.get('due_date', task.get('due_date', ''))
        estimated_hours = request.form.get('estimated_hours', task.get('estimated_hours', 0))
        actual_hours = request.form.get('actual_hours', task.get('actual_hours', 0))
        
        error = None
        
        if not title:
            error = 'Title is required.'
            
        if error is not None:
            flash(error)
        else:
            try:
                # Standardize status and priority
                if status in TASK_STATUS_MAPPING:
                    status = TASK_STATUS_MAPPING[status]
                status = status.upper()
                
                if priority in TASK_PRIORITY_MAPPING:
                    priority = TASK_PRIORITY_MAPPING[priority]
                priority = priority.upper()
                
                # Check if status transition is valid
                if status != task['status'] and not is_valid_status_transition(task['status'], status):
                    flash(f'Invalid status transition from {task["status"]} to {status}')
                    return redirect(url_for('tasks.edit_task', task_id=task_id))
                
                task_data = {
                    'title': title,
                    'description': description,
                    'project_id': project_id,
                    'assigned_to': assigned_to,
                    'status': status,
                    'priority': priority,
                    'due_date': due_date,
                    'estimated_hours': float(estimated_hours) if estimated_hours else 0,
                    'actual_hours': float(actual_hours) if actual_hours else 0,
                }
                
                result = update_task(task_id, task_data)
                
                if result:
                    flash('Task updated successfully!')
                    return redirect(url_for('tasks.view_task', task_id=task_id))
                else:
                    flash('Error updating task')
            except Exception as e:
                flash(f'Error updating task: {str(e)}')
    
    # Get projects and users for dropdowns
    projects = get_all_projects()
    users = get_all_users()  # This function needs to be implemented
    
    return render_template('tasks/edit.html', 
                          task=task,
                          projects=projects,
                          users=users,
                          priorities=TASK_PRIORITIES,
                          statuses=TASK_STATUSES,
                          allowed_transitions=TASK_STATUS_TRANSITIONS.get(task['status'], []))

@bp.route('/<task_id>/delete', methods=('POST',))
@login_required
def delete_task_route(task_id):
    """Delete a task"""
    task = get_task(task_id)
    
    if task is None:
        flash('Task not found')
        return redirect(url_for('tasks.list_tasks'))
    
    # Remember the project ID for redirection
    project_id = task.get('project_id')
    
    if delete_task(task_id):
        flash('Task deleted successfully!')
    else:
        flash('Error deleting task')
    
    # Redirect to project tasks if viewing from a project
    if project_id and request.referrer and 'project' in request.referrer:
        return redirect(url_for('tasks.project_tasks', project_id=project_id))
    else:
        return redirect(url_for('tasks.list_tasks'))

@bp.route('/project/<project_id>')
@login_required
def project_tasks(project_id):
    """View tasks for a specific project"""
    try:
        tasks = get_project_tasks(project_id)
        project = get_project_by_id(project_id)
        
        if not project:
            flash('Project not found')
            return redirect(url_for('projects.list_projects'))
        
        # Get statistics for the project's tasks
        stats = get_task_stats(project_id)
        
        # Get timeline for visualization
        timeline = get_task_timeline(project_id)
        
        return render_template('tasks/project_tasks.html', 
                              tasks=tasks,
                              project=project,
                              stats=stats,
                              timeline=timeline,
                              priorities=TASK_PRIORITIES,
                              statuses=TASK_STATUSES)
    except Exception as e:
        flash(f'Error loading project tasks: {str(e)}')
        return redirect(url_for('projects.view_project', project_id=project_id))

@bp.route('/mytasks')
@login_required
def my_tasks():
    """View tasks assigned to the current user"""
    try:
        user_id = session.get('user_id', 'admin')  # Default to admin for development
        tasks = get_user_tasks(user_id)
        projects = get_all_projects()
        
        # Get status filter
        status_filter = request.args.get('status', '')
        
        # Apply status filter if provided
        if status_filter:
            # Map legacy status to standardized format if needed
            if status_filter in TASK_STATUS_MAPPING:
                status_filter = TASK_STATUS_MAPPING[status_filter]
            status_filter = status_filter.upper()
            
            tasks = [t for t in tasks if t.get('status') == status_filter]
        
        # Get timeline for the user's tasks
        timeline = get_task_timeline()
        
        # Calculate task statistics
        stats = {
            'total': len(tasks),
            'completed': len([t for t in tasks if t['status'] == 'COMPLETED']),
            'in_progress': len([t for t in tasks if t['status'] == 'IN_PROGRESS']),
            'pending': len([t for t in tasks if t['status'] == 'PENDING']),
            'on_hold': len([t for t in tasks if t['status'] == 'ON_HOLD']),
            'cancelled': len([t for t in tasks if t['status'] == 'CANCELED']),
        }
        
        # Calculate overdue tasks
        today = datetime.now().strftime('%Y-%m-%d')
        stats['overdue'] = len([
            t for t in tasks 
            if t.get('due_date') and t['due_date'] < today and t['status'] not in ['COMPLETED', 'CANCELED']
        ])
        
        return render_template('tasks/mytasks.html', 
                              tasks=tasks,
                              projects=projects,
                              timeline=timeline,
                              stats=stats,
                              status_filter=status_filter,
                              priorities=TASK_PRIORITIES,
                              statuses=TASK_STATUSES)
    except Exception as e:
        flash(f'Error loading your tasks: {str(e)}')
        return redirect(url_for('tasks.list_tasks'))

@bp.route('/api/update-status', methods=['POST'])
@login_required
def update_status():
    """API endpoint to update a task's status"""
    data = request.json
    
    if not data or 'task_id' not in data or 'status' not in data:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    task_id = data['task_id']
    new_status = data['status']
    
    # Get the current task
    task = get_task(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    
    # Standardize the new status
    if new_status in TASK_STATUS_MAPPING:
        new_status = TASK_STATUS_MAPPING[new_status]
    new_status = new_status.upper()
    
    # Check if the status transition is valid
    if not is_valid_status_transition(task['status'], new_status):
        return jsonify({
            'success': False, 
            'error': f'Invalid status transition from {task["status"]} to {new_status}'
        }), 400
    
    # Update the task
    result = update_task(task_id, {'status': new_status})
    
    if result:
        return jsonify({
            'success': True, 
            'task': result,
            'status_display': get_status_display(new_status)
        })
    else:
        return jsonify({'success': False, 'error': 'Error updating task'}), 500

@bp.route('/timeline')
@login_required
def task_timeline():
    """View tasks organized by timeline"""
    try:
        # Get filter params
        project_id = request.args.get('project_id', '')
        
        # Get timeline data
        timeline = get_task_timeline(project_id if project_id else None)
        
        # Get all projects for filter
        projects = get_all_projects()
        current_project = get_project_by_id(project_id) if project_id else None
        
        return render_template('tasks/timeline.html',
                             timeline=timeline,
                             projects=projects,
                             current_project=current_project,
                             priorities=TASK_PRIORITIES,
                             statuses=TASK_STATUSES)
    except Exception as e:
        flash(f'Error loading task timeline: {str(e)}')
        return redirect(url_for('tasks.list_tasks'))

@bp.route('/bulk-update', methods=['GET', 'POST'])
@login_required
def bulk_update():
    """Bulk update tasks"""
    if request.method == 'POST':
        task_ids = request.form.getlist('task_ids')
        action = request.form.get('action', '')
        
        if not task_ids or not action:
            flash('No tasks selected or action specified')
            return redirect(url_for('tasks.list_tasks'))
        
        if action.startswith('status_'):
            # Bulk status update
            new_status = action.replace('status_', '')
            
            # Standardize the new status
            if new_status in TASK_STATUS_MAPPING:
                new_status = TASK_STATUS_MAPPING[new_status]
            new_status = new_status.upper()
            
            success_count = 0
            for task_id in task_ids:
                task = get_task(task_id)
                if task and is_valid_status_transition(task['status'], new_status):
                    if update_task(task_id, {'status': new_status}):
                        success_count += 1
            
            if success_count > 0:
                flash(f'Successfully updated {success_count} of {len(task_ids)} tasks to {new_status}')
            else:
                flash('No tasks were updated')
                
        elif action.startswith('priority_'):
            # Bulk priority update
            new_priority = action.replace('priority_', '')
            
            # Standardize the new priority
            if new_priority in TASK_PRIORITY_MAPPING:
                new_priority = TASK_PRIORITY_MAPPING[new_priority]
            new_priority = new_priority.upper()
            
            success_count = 0
            for task_id in task_ids:
                if update_task(task_id, {'priority': new_priority}):
                    success_count += 1
            
            if success_count > 0:
                flash(f'Successfully updated {success_count} of {len(task_ids)} tasks to {new_priority} priority')
            else:
                flash('No tasks were updated')
                
        elif action == 'delete':
            # Bulk delete
            success_count = 0
            for task_id in task_ids:
                if delete_task(task_id):
                    success_count += 1
            
            if success_count > 0:
                flash(f'Successfully deleted {success_count} of {len(task_ids)} tasks')
            else:
                flash('No tasks were deleted')
    
    return redirect(url_for('tasks.list_tasks')) 