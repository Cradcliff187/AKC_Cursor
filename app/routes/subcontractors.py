from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, jsonify
)
from app.routes.auth import login_required
from app.services.subcontractors import (
    get_all_subcontractors, get_subcontractor_by_id, create_subcontractor, 
    update_subcontractor, delete_subcontractor, get_subcontractor_invoices,
    create_invoice, update_invoice, delete_invoice, get_subcontractor_projects
)
from app.services.projects import get_all_projects
from app.services.documents import get_entity_documents, save_uploaded_file, delete_document
import uuid
from datetime import datetime

bp = Blueprint('subcontractors', __name__, url_prefix='/subcontractors')

@bp.route('/')
@login_required
def list_subcontractors():
    """List all subcontractors"""
    try:
        subcontractors = get_all_subcontractors()
        return render_template('subcontractors/index.html', subcontractors=subcontractors)
    except Exception as e:
        flash(f'Error loading subcontractors: {str(e)}')
        return render_template('subcontractors/index.html', subcontractors=[])

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create_subcontractor_route():
    """Create a new subcontractor"""
    if request.method == 'POST':
        name = request.form['name']
        contact_name = request.form['contact_name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        trade = request.form.get('trade', '')
        rate = request.form.get('rate', 0)
        address = request.form.get('address', '')
        insurance_expiry = request.form.get('insurance_expiry', '')
        license = request.form.get('license', '')
        notes = request.form.get('notes', '')
        
        error = None
        
        if not name:
            error = 'Subcontractor name is required.'
            
        if error is not None:
            flash(error)
        else:
            try:
                subcontractor_data = {
                    'name': name,
                    'contact_name': contact_name,
                    'email': email,
                    'phone': phone,
                    'trade': trade,
                    'rate': float(rate) if rate else 0,
                    'address': address,
                    'insurance_expiry': insurance_expiry,
                    'license': license,
                    'notes': notes,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                result = create_subcontractor(subcontractor_data)
                
                if result:
                    flash('Subcontractor created successfully!')
                    return redirect(url_for('subcontractors.list_subcontractors'))
                else:
                    flash('Error creating subcontractor')
            except Exception as e:
                flash(f'Error creating subcontractor: {str(e)}')
    
    return render_template('subcontractors/form.html')

@bp.route('/<subcontractor_id>')
@login_required
def view_subcontractor(subcontractor_id):
    """View a subcontractor's details"""
    try:
        subcontractor = get_subcontractor_by_id(subcontractor_id)
        
        if subcontractor:
            # Get invoices
            invoices = get_subcontractor_invoices(subcontractor_id)
            
            # Get projects
            assigned_projects = get_subcontractor_projects(subcontractor_id)
            
            # Get all projects for dropdown
            all_projects = get_all_projects()
            
            # Get documents
            documents = get_entity_documents('subcontractor', subcontractor_id)
                
            return render_template('subcontractors/detail.html', 
                                  subcontractor=subcontractor, 
                                  invoices=invoices, 
                                  projects=assigned_projects,
                                  all_projects=all_projects,
                                  documents=documents)
        else:
            flash('Subcontractor not found.')
            return redirect(url_for('subcontractors.list_subcontractors'))
    except Exception as e:
        flash(f'Error loading subcontractor: {str(e)}')
        return redirect(url_for('subcontractors.list_subcontractors'))

@bp.route('/<subcontractor_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_subcontractor(subcontractor_id):
    """Edit a subcontractor"""
    if request.method == 'POST':
        name = request.form['name']
        contact_name = request.form['contact_name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        trade = request.form.get('trade', '')
        rate = request.form.get('rate', 0)
        address = request.form.get('address', '')
        insurance_expiry = request.form.get('insurance_expiry', '')
        license = request.form.get('license', '')
        notes = request.form.get('notes', '')
        
        error = None
        
        if not name:
            error = 'Subcontractor name is required.'
            
        if error is not None:
            flash(error)
        else:
            try:
                subcontractor_data = {
                    'name': name,
                    'contact_name': contact_name,
                    'email': email,
                    'phone': phone,
                    'trade': trade,
                    'rate': float(rate) if rate else 0,
                    'address': address,
                    'insurance_expiry': insurance_expiry,
                    'license': license,
                    'notes': notes
                }
                
                result = update_subcontractor(subcontractor_id, subcontractor_data)
                
                if result:
                    flash('Subcontractor updated successfully!')
                    return redirect(url_for('subcontractors.view_subcontractor', subcontractor_id=subcontractor_id))
                else:
                    flash('Error updating subcontractor')
            except Exception as e:
                flash(f'Error updating subcontractor: {str(e)}')
    
    # Get the subcontractor
    try:
        subcontractor = get_subcontractor_by_id(subcontractor_id)
            
        if subcontractor:
            return render_template('subcontractors/form.html', subcontractor=subcontractor)
        else:
            flash('Subcontractor not found.')
            return redirect(url_for('subcontractors.list_subcontractors'))
    except Exception as e:
        flash(f'Error loading subcontractor: {str(e)}')
        return redirect(url_for('subcontractors.list_subcontractors'))

@bp.route('/<subcontractor_id>/delete', methods=('POST',))
@login_required
def delete_subcontractor_route(subcontractor_id):
    """Delete a subcontractor"""
    try:
        success = delete_subcontractor(subcontractor_id)
        
        if success:
            flash('Subcontractor deleted successfully!')
        else:
            flash('Error deleting subcontractor')
    except Exception as e:
        flash(f'Error deleting subcontractor: {str(e)}')
        
    return redirect(url_for('subcontractors.list_subcontractors'))

@bp.route('/invoice', methods=('POST',))
@login_required
def add_invoice():
    """Add an invoice for a subcontractor"""
    subcontractor_id = request.form['subcontractor_id']
    project_id = request.form['project_id']
    invoice_number = request.form['invoice_number']
    amount = request.form['amount']
    date = request.form.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    due_date = request.form.get('due_date', '')
    status = request.form.get('status', 'Pending')
    description = request.form.get('description', '')
    
    try:
        invoice_data = {
            'subcontractor_id': subcontractor_id,
            'project_id': int(project_id),
            'invoice_number': invoice_number,
            'amount': float(amount),
            'date': date,
            'due_date': due_date,
            'status': status,
            'description': description
        }
        
        result = create_invoice(invoice_data)
        
        if result:
            flash('Invoice added successfully!')
        else:
            flash('Error adding invoice')
    except Exception as e:
        flash(f'Error adding invoice: {str(e)}')
        
    return redirect(url_for('subcontractors.view_subcontractor', subcontractor_id=subcontractor_id))

@bp.route('/invoice/<invoice_id>/edit', methods=('POST',))
@login_required
def edit_invoice_route(invoice_id):
    """Edit an invoice"""
    subcontractor_id = request.form['subcontractor_id']
    project_id = request.form['project_id']
    invoice_number = request.form['invoice_number']
    amount = request.form['amount']
    date = request.form.get('date', '')
    due_date = request.form.get('due_date', '')
    status = request.form.get('status', '')
    description = request.form.get('description', '')
    
    try:
        invoice_data = {
            'project_id': int(project_id),
            'invoice_number': invoice_number,
            'amount': float(amount),
            'date': date,
            'due_date': due_date,
            'status': status,
            'description': description
        }
        
        result = update_invoice(invoice_id, invoice_data)
        
        if result:
            flash('Invoice updated successfully!')
        else:
            flash('Error updating invoice')
    except Exception as e:
        flash(f'Error updating invoice: {str(e)}')
        
    return redirect(url_for('subcontractors.view_subcontractor', subcontractor_id=subcontractor_id))

@bp.route('/invoice/<invoice_id>/delete', methods=('POST',))
@login_required
def delete_invoice_route(invoice_id):
    """Delete an invoice"""
    subcontractor_id = request.form['subcontractor_id']
    
    try:
        success = delete_invoice(invoice_id)
        
        if success:
            flash('Invoice deleted successfully!')
        else:
            flash('Error deleting invoice')
    except Exception as e:
        flash(f'Error deleting invoice: {str(e)}')
        
    return redirect(url_for('subcontractors.view_subcontractor', subcontractor_id=subcontractor_id))

@bp.route('/<subcontractor_id>/document/upload', methods=('POST',))
@login_required
def upload_document(subcontractor_id):
    """Upload document for a subcontractor"""
    try:
        subcontractor = get_subcontractor_by_id(subcontractor_id)
        if not subcontractor:
            flash("Subcontractor not found")
            return redirect(url_for('subcontractors.list_subcontractors'))
            
        if 'document' not in request.files:
            flash('No file selected')
            return redirect(url_for('subcontractors.view_subcontractor', subcontractor_id=subcontractor_id))
            
        file = request.files['document']
        
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('subcontractors.view_subcontractor', subcontractor_id=subcontractor_id))
            
        description = request.form.get('description', '')
        
        document = save_uploaded_file(file, 'subcontractor', subcontractor_id, description)
        
        if document:
            flash('Document uploaded successfully')
        else:
            flash('Error uploading document')
            
        return redirect(url_for('subcontractors.view_subcontractor', subcontractor_id=subcontractor_id))
    except Exception as e:
        flash(f'Error uploading document: {str(e)}')
        return redirect(url_for('subcontractors.view_subcontractor', subcontractor_id=subcontractor_id))
        
@bp.route('/document/<document_id>/delete', methods=('POST',))
@login_required
def delete_document_route(document_id):
    """Delete a document"""
    subcontractor_id = request.form['subcontractor_id']
    
    try:
        success = delete_document(document_id)
        
        if success:
            flash('Document deleted successfully')
        else:
            flash('Error deleting document')
    except Exception as e:
        flash(f'Error deleting document: {str(e)}')
        
    return redirect(url_for('subcontractors.view_subcontractor', subcontractor_id=subcontractor_id))

# API Routes
@bp.route('/api', methods=['GET'])
def api_get_all():
    """Get all subcontractors API"""
    subcontractors = get_all_subcontractors()
    return jsonify(subcontractors)

@bp.route('/api/<subcontractor_id>', methods=['GET'])
def api_get_by_id(subcontractor_id):
    """Get subcontractor by ID API"""
    subcontractor = get_subcontractor_by_id(subcontractor_id)
    if not subcontractor:
        return jsonify({"error": "Subcontractor not found"}), 404
    return jsonify(subcontractor)

@bp.route('/api', methods=['POST'])
def api_create():
    """Create subcontractor API"""
    subcontractor_data = request.json
    result = create_subcontractor(subcontractor_data)
    return jsonify(result), 201

@bp.route('/api/<subcontractor_id>', methods=['PUT'])
def api_update(subcontractor_id):
    """Update subcontractor API"""
    subcontractor_data = request.json
    result = update_subcontractor(subcontractor_id, subcontractor_data)
    if not result:
        return jsonify({"error": "Subcontractor not found"}), 404
    return jsonify(result)

@bp.route('/api/<subcontractor_id>', methods=['DELETE'])
def api_delete(subcontractor_id):
    """Delete subcontractor API"""
    success = delete_subcontractor(subcontractor_id)
    if not success:
        return jsonify({"error": "Failed to delete subcontractor"}), 500
    return jsonify({"message": "Subcontractor deleted successfully"})

# Invoice routes
@bp.route('/api/<subcontractor_id>/invoices', methods=['GET'])
def api_get_invoices(subcontractor_id):
    """Get subcontractor invoices API"""
    invoices = get_subcontractor_invoices(subcontractor_id)
    return jsonify(invoices)

@bp.route('/api/invoices', methods=['POST'])
def api_create_invoice():
    """Create invoice API"""
    invoice_data = request.json
    result = create_invoice(invoice_data)
    return jsonify(result), 201

@bp.route('/api/invoices/<invoice_id>', methods=['PUT'])
def api_update_invoice(invoice_id):
    """Update invoice API"""
    invoice_data = request.json
    result = update_invoice(invoice_id, invoice_data)
    if not result:
        return jsonify({"error": "Invoice not found"}), 404
    return jsonify(result)

@bp.route('/api/invoices/<invoice_id>', methods=['DELETE'])
def api_delete_invoice(invoice_id):
    """Delete invoice API"""
    success = delete_invoice(invoice_id)
    if not success:
        return jsonify({"error": "Failed to delete invoice"}), 500
    return jsonify({"message": "Invoice deleted successfully"}) 