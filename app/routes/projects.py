from flask import (
    Blueprint, flash, g, redirect, render_template, 
    request, session, url_for, jsonify
)
from app.routes.auth import login_required
from app.services.projects import (
    get_all_projects, get_project_by_id, create_project,
    update_project, delete_project, get_project_tasks
)
from datetime import datetime

bp = Blueprint('projects', __name__, url_prefix='/projects')

@bp.route('/')
@login_required
def list_projects():
    # Get user projects
    user_id = session.get('user_id')
    projects = get_all_projects()  # Ideally filter by user access
    
    return render_template('project_list.html', projects=projects)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        client = request.form['client']
        status = request.form['status']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        budget = request.form.get('budget', 0)
        location = request.form['location']
        
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
                'client': client,
                'status': status,
                'start_date': start_date,
                'end_date': end_date,
                'budget': float(budget) if budget else 0.0,
                'budget_spent': 0.0,
                'location': location,
                'user_id': session.get('user_id'),
                'created_at': datetime.utcnow().isoformat(),
                # Calculate progress based on status
                'progress': 100 if status == 'Completed' else (
                    75 if status == 'In Progress' else (
                    25 if status == 'Planning' else 0
                ))
            }
            
            # Create the project
            project = create_project(project_data)
            
            if project:
                flash('Project created successfully!')
                return redirect(url_for('projects.view_project', project_id=project['id']))
            else:
                flash('Failed to create project.')
    
    return render_template('create_project.html')

@bp.route('/<int:project_id>')
@login_required
def view_project(project_id):
    project = get_project_by_id(project_id)
    
    if project is None:
        flash('Project not found.')
        return redirect(url_for('projects.list_projects'))
    
    # Get project tasks
    tasks = get_project_tasks(project_id)
    
    return render_template('project_detail.html', project=project, tasks=tasks)

@bp.route('/<int:project_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_project(project_id):
    project = get_project_by_id(project_id)
    
    if project is None:
        flash('Project not found.')
        return redirect(url_for('projects.list_projects'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        client = request.form['client']
        status = request.form['status']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        budget = request.form.get('budget', 0)
        location = request.form['location']
        
        error = None
        
        if not name:
            error = 'Project name is required.'
        
        if error is not None:
            flash(error)
        else:
            # Calculate progress based on status
            progress = 100 if status == 'Completed' else (
                75 if status == 'In Progress' else (
                25 if status == 'Planning' else 0
            ))
            
            # Prepare project data
            project_data = {
                'name': name,
                'description': description,
                'client': client,
                'status': status,
                'start_date': start_date,
                'end_date': end_date,
                'budget': float(budget) if budget else 0.0,
                'location': location,
                'progress': progress
            }
            
            # Update the project
            updated_project = update_project(project_id, project_data)
            
            if updated_project:
                flash('Project updated successfully!')
                return redirect(url_for('projects.view_project', project_id=project_id))
            else:
                flash('Failed to update project.')
    
    return render_template('edit_project.html', project=project)

@bp.route('/<int:project_id>/delete', methods=('POST',))
@login_required
def delete_project(project_id):
    project = get_project_by_id(project_id)
    
    if project is None:
        flash('Project not found.')
        return redirect(url_for('projects.list_projects'))
    
    # Delete the project
    if delete_project(project_id):
        flash('Project deleted successfully!')
    else:
        flash('Failed to delete project.')
    
    return redirect(url_for('projects.list_projects')) 