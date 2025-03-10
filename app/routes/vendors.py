from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, jsonify
)
from app.routes.auth import login_required
from app.services.vendors import (
    get_all_vendors, get_vendor_by_id, create_vendor, 
    update_vendor, delete_vendor, get_vendor_purchases,
    add_purchase, update_purchase, delete_purchase
)
from app.services.projects import get_all_projects
from app.services.documents import get_entity_documents, save_uploaded_file, delete_document
import uuid
from datetime import datetime
import os

bp = Blueprint('vendors', __name__, url_prefix='/vendors')

@bp.route('/')
@login_required
def list_vendors():
    """List all vendors"""
    try:
        vendors = get_all_vendors()
        return render_template('vendors/index.html', vendors=vendors)
    except Exception as e:
        flash(f'Error loading vendors: {str(e)}')
        return render_template('vendors/index.html', vendors=[])

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create_vendor():
    """Create a new vendor"""
    if request.method == 'POST':
        name = request.form['name']
        contact_name = request.form['contact_name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        notes = request.form.get('notes', '')
        
        error = None
        
        if not name:
            error = 'Vendor name is required.'
            
        if error is not None:
            flash(error)
        else:
            try:
                vendor_data = {
                    'name': name,
                    'contact_name': contact_name,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'notes': notes,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                result = create_vendor(vendor_data)
                
                if result:
                    flash('Vendor created successfully!')
                    return redirect(url_for('vendors.list_vendors'))
                else:
                    flash('Error creating vendor')
            except Exception as e:
                flash(f'Error creating vendor: {str(e)}')
    
    return render_template('vendors/create.html')

@bp.route('/<vendor_id>')
@login_required
def view_vendor(vendor_id):
    """View a vendor's details"""
    try:
        vendor = get_vendor_by_id(vendor_id)
        
        if vendor:
            purchases = get_vendor_purchases(vendor_id)
            projects = get_all_projects()
            documents = get_entity_documents('vendor', vendor_id)
                
            return render_template('vendors/detail.html', 
                                   vendor=vendor, 
                                   purchases=purchases, 
                                   projects=projects,
                                   documents=documents)
        else:
            flash('Vendor not found.')
            return redirect(url_for('vendors.list_vendors'))
    except Exception as e:
        flash(f'Error loading vendor: {str(e)}')
        return redirect(url_for('vendors.list_vendors'))

@bp.route('/<vendor_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_vendor(vendor_id):
    """Edit a vendor"""
    if request.method == 'POST':
        name = request.form['name']
        contact_name = request.form['contact_name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        notes = request.form.get('notes', '')
        
        error = None
        
        if not name:
            error = 'Vendor name is required.'
            
        if error is not None:
            flash(error)
        else:
            try:
                vendor_data = {
                    'name': name,
                    'contact_name': contact_name,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'notes': notes
                }
                
                result = update_vendor(vendor_id, vendor_data)
                
                if result:
                    flash('Vendor updated successfully!')
                    return redirect(url_for('vendors.view_vendor', vendor_id=vendor_id))
                else:
                    flash('Error updating vendor')
            except Exception as e:
                flash(f'Error updating vendor: {str(e)}')
    
    # Get the vendor
    try:
        vendor = get_vendor_by_id(vendor_id)
            
        if vendor:
            return render_template('vendors/edit.html', vendor=vendor)
        else:
            flash('Vendor not found.')
            return redirect(url_for('vendors.list_vendors'))
    except Exception as e:
        flash(f'Error loading vendor: {str(e)}')
        return redirect(url_for('vendors.list_vendors'))

@bp.route('/<vendor_id>/delete', methods=('POST',))
@login_required
def delete_vendor(vendor_id):
    """Delete a vendor"""
    try:
        success = delete_vendor(vendor_id)
        
        if success:
            flash('Vendor deleted successfully!')
        else:
            flash('Error deleting vendor')
    except Exception as e:
        flash(f'Error deleting vendor: {str(e)}')
        
    return redirect(url_for('vendors.list_vendors'))

@bp.route('/purchase', methods=('POST',))
@login_required
def add_purchase_route():
    """Add a purchase record for a vendor"""
    vendor_id = request.form['vendor_id']
    project_id = request.form['project_id']
    description = request.form['description']
    amount = request.form['amount']
    date = request.form.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    
    try:
        purchase_data = {
            'vendor_id': vendor_id,
            'project_id': int(project_id),
            'description': description,
            'amount': float(amount),
            'date': date
        }
        
        result = add_purchase(purchase_data)
        
        if result:
            flash('Purchase added successfully!')
        else:
            flash('Error adding purchase')
    except Exception as e:
        flash(f'Error adding purchase: {str(e)}')
        
    return redirect(url_for('vendors.view_vendor', vendor_id=vendor_id))

@bp.route('/purchase/<purchase_id>/edit', methods=('POST',))
@login_required
def edit_purchase(purchase_id):
    """Edit a purchase record"""
    vendor_id = request.form['vendor_id']
    project_id = request.form['project_id']
    description = request.form['description']
    amount = request.form['amount']
    date = request.form.get('date', '')
    
    try:
        purchase_data = {
            'project_id': int(project_id),
            'description': description,
            'amount': float(amount),
            'date': date
        }
        
        result = update_purchase(purchase_id, purchase_data)
        
        if result:
            flash('Purchase updated successfully!')
        else:
            flash('Error updating purchase')
    except Exception as e:
        flash(f'Error updating purchase: {str(e)}')
        
    return redirect(url_for('vendors.view_vendor', vendor_id=vendor_id))

@bp.route('/purchase/<purchase_id>/delete', methods=('POST',))
@login_required
def delete_purchase_route(purchase_id):
    """Delete a purchase record"""
    vendor_id = request.form['vendor_id']
    
    try:
        success = delete_purchase(purchase_id)
        
        if success:
            flash('Purchase deleted successfully!')
        else:
            flash('Error deleting purchase')
    except Exception as e:
        flash(f'Error deleting purchase: {str(e)}')
        
    return redirect(url_for('vendors.view_vendor', vendor_id=vendor_id))

@bp.route('/<vendor_id>/document/upload', methods=('POST',))
@login_required
def upload_document(vendor_id):
    """Upload document for a vendor"""
    try:
        vendor = get_vendor_by_id(vendor_id)
        if not vendor:
            flash("Vendor not found")
            return redirect(url_for('vendors.list_vendors'))
            
        if 'document' not in request.files:
            flash('No file selected')
            return redirect(url_for('vendors.view_vendor', vendor_id=vendor_id))
            
        file = request.files['document']
        
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('vendors.view_vendor', vendor_id=vendor_id))
            
        description = request.form.get('description', '')
        
        document = save_uploaded_file(file, 'vendor', vendor_id, description)
        
        if document:
            flash('Document uploaded successfully')
        else:
            flash('Error uploading document')
            
        return redirect(url_for('vendors.view_vendor', vendor_id=vendor_id))
    except Exception as e:
        flash(f'Error uploading document: {str(e)}')
        return redirect(url_for('vendors.view_vendor', vendor_id=vendor_id))
        
@bp.route('/document/<document_id>/delete', methods=('POST',))
@login_required
def delete_document_route(document_id):
    """Delete a document"""
    vendor_id = request.form['vendor_id']
    
    try:
        success = delete_document(document_id)
        
        if success:
            flash('Document deleted successfully')
        else:
            flash('Error deleting document')
    except Exception as e:
        flash(f'Error deleting document: {str(e)}')
        
    return redirect(url_for('vendors.view_vendor', vendor_id=vendor_id))

# API Routes
@bp.route('/api', methods=['GET'])
def api_get_all():
    """Get all vendors API"""
    try:
        vendors = get_all_vendors()
        return jsonify(vendors)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/<vendor_id>', methods=['GET'])
def api_get_by_id(vendor_id):
    """Get vendor by ID API"""
    try:
        vendor = get_vendor_by_id(vendor_id)
        if not vendor:
            return jsonify({"error": "Vendor not found"}), 404
        return jsonify(vendor)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api', methods=['POST'])
def api_create():
    """Create vendor API"""
    try:
        vendor_data = request.json
        result = create_vendor(vendor_data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/<vendor_id>', methods=['PUT'])
def api_update(vendor_id):
    """Update vendor API"""
    try:
        vendor_data = request.json
        result = update_vendor(vendor_id, vendor_data)
        if not result:
            return jsonify({"error": "Vendor not found"}), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/<vendor_id>', methods=['DELETE'])
def api_delete(vendor_id):
    """Delete vendor API"""
    try:
        success = delete_vendor(vendor_id)
        if not success:
            return jsonify({"error": "Failed to delete vendor"}), 500
        return jsonify({"message": "Vendor deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/<vendor_id>/purchases', methods=['GET'])
def api_get_purchases(vendor_id):
    """Get vendor purchases API"""
    try:
        purchases = get_vendor_purchases(vendor_id)
        return jsonify(purchases)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/purchases', methods=['POST'])
def api_create_purchase():
    """Create purchase API"""
    try:
        purchase_data = request.json
        result = add_purchase(purchase_data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/purchases/<purchase_id>', methods=['PUT'])
def api_update_purchase(purchase_id):
    """Update purchase API"""
    try:
        purchase_data = request.json
        result = update_purchase(purchase_id, purchase_data)
        if not result:
            return jsonify({"error": "Purchase not found"}), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/purchases/<purchase_id>', methods=['DELETE'])
def api_delete_purchase(purchase_id):
    """Delete purchase API"""
    try:
        success = delete_purchase(purchase_id)
        if not success:
            return jsonify({"error": "Failed to delete purchase"}), 500
        return jsonify({"message": "Purchase deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500 