from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, jsonify
)
from app.routes.auth import login_required
from app.services.clients import (
    get_all_clients, get_client_by_id, create_client,
    update_client, delete_client, get_client_projects
)
import uuid
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from app.utils import allowed_file

bp = Blueprint('clients', __name__, url_prefix='/clients')

@bp.route('/')
@login_required
def list_clients():
    """List all clients"""
    clients = get_all_clients()
    return render_template('clients/index.html', clients=clients)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create_client():
    """Create a new client"""
    if request.method == 'POST':
        name = request.form['name']
        contact_name = request.form['contact_name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        notes = request.form.get('notes', '')
        
        error = None
        
        if not name:
            error = 'Client name is required.'
            
        if error is not None:
            flash(error)
        else:
            try:
                client_data = {
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'contact_name': contact_name,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'notes': notes,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                new_client = create_client(client_data)
                if new_client:
                    flash('Client created successfully!')
                    return redirect(url_for('clients.list_clients'))
                else:
                    flash('Error creating client')
            except Exception as e:
                flash(f'Error creating client: {str(e)}')
    
    return render_template('clients/create.html')

@bp.route('/<string:id>')
@login_required
def view_client(id):
    """View a client's details"""
    client = get_client_by_id(id)
    
    if client:
        # Get projects for this client
        projects = get_client_projects(id)
        return render_template('clients/detail.html', client=client, projects=projects)
    else:
        flash('Client not found.')
        return redirect(url_for('clients.list_clients'))

@bp.route('/<string:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_client(id):
    """Edit a client"""
    client = get_client_by_id(id)
    
    if not client:
        flash('Client not found.')
        return redirect(url_for('clients.list_clients'))
        
    if request.method == 'POST':
        name = request.form['name']
        contact_name = request.form['contact_name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        notes = request.form.get('notes', '')
        
        error = None
        
        if not name:
            error = 'Client name is required.'
            
        if error is not None:
            flash(error)
        else:
            try:
                client_data = {
                    'name': name,
                    'contact_name': contact_name,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'notes': notes
                }
                
                updated_client = update_client(id, client_data)
                if updated_client:
                    flash('Client updated successfully!')
                    return redirect(url_for('clients.view_client', id=id))
                else:
                    flash('Error updating client')
            except Exception as e:
                flash(f'Error updating client: {str(e)}')
    
    return render_template('clients/edit.html', client=client)

@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete_client(id):
    """Delete a client"""
    success = delete_client(id)
    
    if success:
        flash('Client deleted successfully!')
    else:
        flash('Error deleting client')
        
    return redirect(url_for('clients.list_clients')) 