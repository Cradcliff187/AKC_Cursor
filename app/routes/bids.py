from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, jsonify, send_from_directory,
    current_app, abort
)
from werkzeug.utils import secure_filename
from app.routes.auth import login_required
from app.services.bids import (
    get_all_bids, get_bid_by_id, get_bid_items, create_bid, 
    update_bid, delete_bid, calculate_bid_totals, save_bid_document,
    get_bid_versions, get_bid_version_data, convert_bid_to_project
)
from app.services.clients import get_all_clients, get_client_by_id
from app.services.projects import get_all_projects, get_project_by_id
from app.models.bid import Bid
from app.models.bid_item import BidItem
from datetime import datetime
import os
import json

bp = Blueprint('bids', __name__, url_prefix='/bids')

@bp.route('/')
@login_required
def list_bids():
    """List all bids and proposals"""
    status_filter = request.args.get('status')
    client_id = request.args.get('client_id')
    
    bids = get_all_bids(status=status_filter, client_id=client_id)
    clients = get_all_clients()
    
    return render_template(
        'bids/list.html', 
        bids=bids, 
        clients=clients,
        current_status=status_filter,
        current_client_id=client_id
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_bid_route():
    """Create a new bid or proposal"""
    if request.method == 'POST':
        name = request.form.get('name')
        client_id = request.form.get('client_id')
        description = request.form.get('description')
        
        if not name:
            flash('Name is required', 'error')
            return redirect(url_for('bids.create_bid_route'))
        
        # Gather bid data from form
        bid_data = {
            'name': name,
            'client_id': client_id,
            'description': description,
            'proposal_date': request.form.get('proposal_date', datetime.now().strftime('%Y-%m-%d')),
            'valid_until': request.form.get('valid_until'),
            'terms_and_conditions': request.form.get('terms_and_conditions'),
            'notes': request.form.get('notes'),
            'created_by_id': session.get('user_id'),
            'status': 'Draft'
        }
        
        # Create the bid
        bid_id = create_bid(bid_data)
        
        # Handle file upload if present
        if 'document' in request.files and request.files['document'].filename:
            save_bid_document(bid_id, request.files['document'])
        
        flash('Bid created successfully. Now you can add line items.', 'success')
        return redirect(url_for('bids.edit_bid', bid_id=bid_id))
    
    # GET request - show the create form
    clients = get_all_clients()
    return render_template('bids/create.html', clients=clients)

@bp.route('/<int:bid_id>')
@login_required
def view_bid(bid_id):
    """View a bid or proposal"""
    bid = get_bid_by_id(bid_id)
    if not bid:
        flash('Bid not found', 'error')
        return redirect(url_for('bids.list_bids'))
    
    # Get bid items
    items = get_bid_items(bid_id)
    
    # Group items by type for easy display
    grouped_items = {
        'Labor': [],
        'Material': [],
        'Other': []
    }
    
    for item in items:
        if item['item_type'] in grouped_items:
            grouped_items[item['item_type']].append(item)
        else:
            grouped_items['Other'].append(item)
    
    # Get bid versions
    versions = get_bid_versions(bid_id)
    
    # Determine if this bid can be converted to a project
    can_convert = bid['status'] == 'Accepted' and not bid['project_id']
    
    return render_template(
        'bids/detail.html', 
        bid=bid, 
        items=items,
        grouped_items=grouped_items,
        versions=versions,
        can_convert=can_convert
    )

@bp.route('/<int:bid_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bid(bid_id):
    """Edit an existing bid"""
    bid = get_bid_by_id(bid_id)
    if not bid:
        flash('Bid not found', 'error')
        return redirect(url_for('bids.list_bids'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        client_id = request.form.get('client_id')
        
        if not name:
            flash('Name is required', 'error')
            return redirect(url_for('bids.edit_bid', bid_id=bid_id))
        
        # Gather bid data from form
        bid_data = {
            'name': name,
            'client_id': client_id,
            'description': request.form.get('description'),
            'proposal_date': request.form.get('proposal_date'),
            'valid_until': request.form.get('valid_until'),
            'terms_and_conditions': request.form.get('terms_and_conditions'),
            'notes': request.form.get('notes'),
            'status': request.form.get('status', bid['status']),
            'created_by_id': session.get('user_id')
        }
        
        # Update the bid
        update_bid(bid_id, bid_data)
        
        # Handle file upload if present
        if 'document' in request.files and request.files['document'].filename:
            save_bid_document(bid_id, request.files['document'])
        
        flash('Bid updated successfully', 'success')
        return redirect(url_for('bids.view_bid', bid_id=bid_id))
    
    # GET request - show the edit form
    clients = get_all_clients()
    items = get_bid_items(bid_id)
    
    return render_template(
        'bids/edit.html', 
        bid=bid, 
        clients=clients,
        items=items
    )

@bp.route('/<int:bid_id>/delete', methods=['POST'])
@login_required
def delete_bid_route(bid_id):
    """Delete a bid"""
    bid = get_bid_by_id(bid_id)
    if not bid:
        flash('Bid not found', 'error')
        return redirect(url_for('bids.list_bids'))
    
    # Check if bid has a project attached
    if bid['project_id']:
        flash('Cannot delete a bid that has been converted to a project', 'error')
        return redirect(url_for('bids.view_bid', bid_id=bid_id))
    
    # Delete the bid
    delete_bid(bid_id)
    
    flash('Bid deleted successfully', 'success')
    return redirect(url_for('bids.list_bids'))

@bp.route('/<int:bid_id>/items', methods=['GET', 'POST'])
@login_required
def manage_bid_items(bid_id):
    """Manage bid items (line items)"""
    bid = get_bid_by_id(bid_id)
    if not bid:
        flash('Bid not found', 'error')
        return redirect(url_for('bids.list_bids'))
    
    if request.method == 'POST':
        # Process form data for adding or updating items
        if 'item_data' in request.form:
            # Parse JSON data from form
            try:
                items_data = json.loads(request.form['item_data'])
                
                # Update bid with new items
                update_bid(bid_id, {}, items_data)
                
                # Recalculate totals
                calculate_bid_totals(bid_id)
                
                return jsonify({'success': True, 'message': 'Items updated successfully'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error updating items: {str(e)}'})
        else:
            flash('No item data received', 'error')
            return redirect(url_for('bids.manage_bid_items', bid_id=bid_id))
    
    # GET request - show the items management page
    items = get_bid_items(bid_id)
    
    return render_template(
        'bids/items.html', 
        bid=bid, 
        items=items
    )

@bp.route('/<int:bid_id>/download')
@login_required
def download_bid_document(bid_id):
    """Download the document attached to a bid"""
    bid = get_bid_by_id(bid_id)
    if not bid or not bid['file_path'] or not bid['original_filename']:
        flash('Document not found', 'error')
        return redirect(url_for('bids.view_bid', bid_id=bid_id))
    
    # Extract directory and filename
    directory = os.path.dirname(bid['file_path'])
    filename = os.path.basename(bid['file_path'])
    
    return send_from_directory(
        directory, 
        filename, 
        as_attachment=True, 
        download_name=bid['original_filename']
    )

@bp.route('/<int:bid_id>/version/<int:version>')
@login_required
def view_bid_version(bid_id, version):
    """View a specific version of a bid"""
    bid = get_bid_by_id(bid_id)
    if not bid:
        flash('Bid not found', 'error')
        return redirect(url_for('bids.list_bids'))
    
    version_data = get_bid_version_data(bid_id, version)
    if not version_data:
        flash('Version not found', 'error')
        return redirect(url_for('bids.view_bid', bid_id=bid_id))
    
    return render_template(
        'bids/version.html', 
        bid=bid,
        version=version_data
    )

@bp.route('/<int:bid_id>/convert', methods=['GET', 'POST'])
@login_required
def convert_to_project(bid_id):
    """Convert an accepted bid to a project"""
    bid = get_bid_by_id(bid_id)
    if not bid:
        flash('Bid not found', 'error')
        return redirect(url_for('bids.list_bids'))
    
    # Check if bid can be converted
    if bid['status'] != 'Accepted':
        flash('Only accepted bids can be converted to projects', 'error')
        return redirect(url_for('bids.view_bid', bid_id=bid_id))
    
    if bid['project_id']:
        flash('This bid has already been converted to a project', 'error')
        return redirect(url_for('bids.view_bid', bid_id=bid_id))
    
    if request.method == 'POST':
        # Gather project data from form
        project_data = {
            'name': request.form.get('name', bid['name']),
            'client_id': bid['client_id'],
            'description': request.form.get('description', bid['description']),
            'budget': bid['total_amount'],
            'status': request.form.get('status', 'Planning'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date')
        }
        
        # Convert bid to project
        result = convert_bid_to_project(bid_id, project_data)
        
        if result and result.get('success'):
            flash(result.get('message', 'Bid converted to project successfully'), 'success')
            return redirect(url_for('projects.view', project_id=result.get('project_id')))
        else:
            flash(result.get('message', 'Failed to convert bid to project'), 'error')
            return redirect(url_for('bids.view_bid', bid_id=bid_id))
    
    # GET request - show conversion form
    return render_template(
        'bids/convert.html', 
        bid=bid
    )

@bp.route('/<int:bid_id>/respond', methods=['POST'])
@login_required
def client_response(bid_id):
    """Record a client's response to a bid"""
    bid = get_bid_by_id(bid_id)
    if not bid:
        flash('Bid not found', 'error')
        return redirect(url_for('bids.list_bids'))
    
    response = request.form.get('response')
    if not response or response not in ['Accepted', 'Rejected', 'Reviewing']:
        flash('Invalid response', 'error')
        return redirect(url_for('bids.view_bid', bid_id=bid_id))
    
    # Update bid with client response
    bid_data = {
        'status': response,
        'client_response': request.form.get('client_response_notes'),
        'client_response_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    update_bid(bid_id, bid_data)
    
    flash(f'Bid marked as {response}', 'success')
    return redirect(url_for('bids.view_bid', bid_id=bid_id))

@bp.route('/client/<int:client_id>')
@login_required
def client_bids(client_id):
    """List bids for a specific client"""
    client = get_client_by_id(client_id)
    if not client:
        flash('Client not found', 'error')
        return redirect(url_for('bids.list_bids'))
    
    bids = get_all_bids(client_id=client_id)
    
    return render_template(
        'bids/client_bids.html', 
        bids=bids, 
        client=client
    )

@bp.route('/api/items/<int:bid_id>')
@login_required
def api_get_bid_items(bid_id):
    """API endpoint to get bid items as JSON"""
    items = get_bid_items(bid_id)
    return jsonify(items)

@bp.route('/api/calculate/<int:bid_id>', methods=['POST'])
@login_required
def api_calculate_totals(bid_id):
    """API endpoint to calculate bid totals"""
    totals = calculate_bid_totals(bid_id)
    return jsonify(totals) 