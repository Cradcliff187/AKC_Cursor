from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, jsonify
)
from app.routes.auth import login_required
from app.services.supabase import supabase
from app.services.time import (
    get_all_time_entries, get_user_time_entries, get_time_entry,
    create_time_entry, update_time_entry, delete_time_entry,
    update_time_entry_status, get_time_summary
)
from app.services.projects import get_all_projects
from datetime import datetime
import uuid

bp = Blueprint('time', __name__, url_prefix='/time')

@bp.route('/')
@login_required
def list_entries():
    """Show list of all time entries for the current user"""
    try:
        user_id = session.get('user_id', 'admin')  # Default to admin for development
        time_entries = get_user_time_entries(user_id)
        projects = get_all_projects()
        
        # Get time summary
        summary = get_time_summary(user_id)
        
        return render_template('time/list.html', 
                               time_entries=time_entries, 
                               projects=projects,
                               total_hours=summary['total_hours'],
                               billable_hours=summary['billable_hours'],
                               today=datetime.now().strftime('%Y-%m-%d'))
    except Exception as e:
        flash(f'Error loading time entries: {str(e)}')
        return render_template('time/list.html', 
                               time_entries=[], 
                               projects=[],
                               total_hours=0,
                               billable_hours=0,
                               today=datetime.now().strftime('%Y-%m-%d'))

@bp.route('/log', methods=('GET', 'POST'))
@login_required
def log_time():
    """Log new time entry"""
    if request.method == 'POST':
        user_id = session.get('user_id', 'admin')  # Default to admin for development
        project_id = request.form['project_id']
        date = request.form['date']
        hours = request.form['hours']
        description = request.form['description']
        billable = 'billable' in request.form
        
        try:
            time_entry = {
                'user_id': user_id,
                'project_id': project_id,
                'date': date,
                'hours': float(hours),
                'description': description,
                'billable': billable
            }
            
            result = create_time_entry(time_entry)
            
            if result:
                flash('Time entry logged successfully!')
            else:
                flash('Error creating time entry')
                
            return redirect(url_for('time.list_entries'))
        except Exception as e:
            flash(f'Error logging time: {str(e)}')
    
    # Get projects for the dropdown
    projects = get_all_projects()
    return render_template('time/log.html', projects=projects, today=datetime.now().strftime('%Y-%m-%d'))

@bp.route('/edit/<entry_id>', methods=('GET', 'POST'))
@login_required
def edit_time_entry(entry_id):
    """Edit an existing time entry"""
    if request.method == 'POST':
        project_id = request.form['project_id']
        date = request.form['date']
        hours = request.form['hours']
        description = request.form['description']
        billable = 'billable' in request.form
        
        try:
            time_entry = {
                'project_id': project_id,
                'date': date,
                'hours': float(hours),
                'description': description,
                'status': 'pending',  # Reset to pending since it was modified
                'billable': billable
            }
            
            result = update_time_entry(entry_id, time_entry)
            
            if result:
                flash('Time entry updated successfully!')
            else:
                flash('Error updating time entry')
                
            return redirect(url_for('time.list_entries'))
        except Exception as e:
            flash(f'Error updating time entry: {str(e)}')
    
    # Get the time entry and projects
    time_entry = get_time_entry(entry_id)
    if not time_entry:
        flash('Time entry not found')
        return redirect(url_for('time.list_entries'))
        
    projects = get_all_projects()
    return render_template('time/edit.html', time_entry=time_entry, projects=projects)

@bp.route('/delete/<entry_id>', methods=('POST',))
@login_required
def delete_time(entry_id):
    """Delete a time entry"""
    try:
        success = delete_time_entry(entry_id)
        
        if success:
            flash('Time entry deleted successfully!')
        else:
            flash('Error deleting time entry')
    except Exception as e:
        flash(f'Error deleting time entry: {str(e)}')
        
    return redirect(url_for('time.list_entries'))

@bp.route('/status/update', methods=['POST'])
@login_required
def update_time_status():
    """Update the status of a time entry (API endpoint)"""
    data = request.json
    entry_id = data.get('entry_id')
    status = data.get('status')
    
    if not entry_id or not status:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
    try:
        result = update_time_entry_status(entry_id, status)
        
        if result:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'message': 'Entry not found or update failed'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/myentries')
@login_required
def user_time():
    """View current user's time entries"""
    user_id = session.get('user_id', 'admin')  # Default to admin for development
    
    try:
        time_entries = get_user_time_entries(user_id)
        projects = get_all_projects()
        
        # Get time summary
        summary = get_time_summary(user_id)
        
        return render_template('time/user.html', 
                              time_entries=time_entries, 
                              projects=projects,
                              user_id=user_id,
                              total_hours=summary['total_hours'],
                              billable_hours=summary['billable_hours'])
    except Exception as e:
        flash(f'Error loading user time entries: {str(e)}')
        return redirect(url_for('time.list_entries'))

@bp.route('/reports')
@login_required
def reports():
    """Show time reports"""
    user_id = session.get('user_id')
    
    try:
        # Get all time entries
        if supabase:
            response = supabase.from_("time_entries").select("*, projects(name)").execute()
            time_entries = response.data
        else:
            # Mock time entries
            time_entries = [
                {
                    'id': '1', 
                    'user_id': user_id,
                    'project_id': 1,
                    'date': '2023-03-01',
                    'hours': 8,
                    'description': 'Site preparation and initial groundwork',
                    'status': 'Approved',
                    'created_at': '2023-03-01T08:00:00',
                    'projects': {'name': 'Sample Project 1'}
                },
                {
                    'id': '2', 
                    'user_id': user_id,
                    'project_id': 2,
                    'date': '2023-03-02',
                    'hours': 6,
                    'description': 'Client meeting and project planning',
                    'status': 'Pending',
                    'created_at': '2023-03-02T09:00:00',
                    'projects': {'name': 'Sample Project 2'}
                }
            ]
            
        # Get all projects
        if supabase:
            project_response = supabase.from_("projects").select("*").execute()
            projects = project_response.data
        else:
            # Mock projects
            projects = [
                {'id': 1, 'name': 'Sample Project 1'},
                {'id': 2, 'name': 'Sample Project 2'},
                {'id': 3, 'name': 'Completed Example'}
            ]
            
        # Get all users
        if supabase:
            user_response = supabase.from_("users").select("*").execute()
            users = user_response.data
        else:
            # Mock users
            users = [
                {'id': 1, 'first_name': 'Admin', 'last_name': 'User', 'email': 'admin@example.com'}
            ]
            
        return render_template('time/reports.html', time_entries=time_entries, projects=projects, users=users)
    except Exception as e:
        flash(f'Error loading reports: {str(e)}')
        return render_template('time/reports.html', time_entries=[], projects=[], users=[])

@bp.route('/project/<int:project_id>')
@login_required
def project_time(project_id):
    """Show time entries for a specific project"""
    try:
        # Get project details
        if supabase:
            project_response = supabase.from_("projects").select("*").eq("id", project_id).execute()
            project = project_response.data[0] if project_response.data else None
        else:
            # Mock project
            project = {'id': project_id, 'name': 'Sample Project', 'status': 'In Progress'}
            
        # Get time entries for this project
        if supabase:
            entry_response = supabase.from_("time_entries").select("*, users(first_name, last_name)").eq("project_id", project_id).execute()
            time_entries = entry_response.data
        else:
            # Mock time entries
            time_entries = [
                {
                    'id': '1', 
                    'user_id': 1,
                    'project_id': project_id,
                    'date': '2023-03-01',
                    'hours': 8,
                    'description': 'Site preparation and initial groundwork',
                    'status': 'Approved',
                    'created_at': '2023-03-01T08:00:00',
                    'users': {'first_name': 'Admin', 'last_name': 'User'}
                },
                {
                    'id': '2', 
                    'user_id': 1,
                    'project_id': project_id,
                    'date': '2023-03-02',
                    'hours': 6,
                    'description': 'Client meeting and project planning',
                    'status': 'Pending',
                    'created_at': '2023-03-02T09:00:00',
                    'users': {'first_name': 'Admin', 'last_name': 'User'}
                }
            ]
            
        return render_template('time/project.html', project=project, time_entries=time_entries)
    except Exception as e:
        flash(f'Error loading project time entries: {str(e)}')
        return redirect(url_for('time.reports')) 