from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, jsonify, send_from_directory,
    current_app, abort
)
from werkzeug.utils import secure_filename
from app.routes.auth import login_required
from app.services.invoices import (
    get_all_invoices, get_invoice_by_id, get_invoice_items, create_invoice, 
    update_invoice, delete_invoice, get_invoice_payments, record_payment,
    delete_payment, mark_invoice_as_sent, mark_invoice_as_cancelled,
    get_overdue_invoices, get_upcoming_invoices, send_invoice_email
)
from app.services.clients import get_all_clients, get_client_by_id
from app.services.projects import get_all_projects, get_project_by_id
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.payment import Payment
from datetime import datetime, timedelta
import os
import json

bp = Blueprint('invoices', __name__, url_prefix='/invoices')

@bp.route('/')
@login_required
def list_invoices():
    """List all invoices with filtering options"""
    status_filter = request.args.get('status')
    client_id = request.args.get('client_id')
    project_id = request.args.get('project_id')
    
    # Date filtering
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    invoices = get_all_invoices(
        status=status_filter, 
        client_id=client_id, 
        project_id=project_id,
        date_from=date_from,
        date_to=date_to
    )
    
    clients = get_all_clients()
    projects = get_all_projects()
    
    return render_template(
        'invoices/list.html', 
        invoices=invoices, 
        clients=clients,
        projects=projects,
        current_status=status_filter,
        current_client_id=client_id,
        current_project_id=project_id,
        date_from=date_from,
        date_to=date_to
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_invoice_route():
    """Create a new invoice"""
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        project_id = request.form.get('project_id', None) or None  # Convert empty string to None
        issue_date = request.form.get('issue_date')
        due_date = request.form.get('due_date')
        tax_rate = request.form.get('tax_rate', 0)
        
        if not client_id:
            flash('Client is required', 'error')
            return redirect(url_for('invoices.create_invoice_route'))
        
        # Gather invoice data from form
        invoice_data = {
            'client_id': client_id,
            'project_id': project_id,
            'issue_date': issue_date,
            'due_date': due_date,
            'tax_rate': tax_rate,
            'notes': request.form.get('notes'),
            'terms': request.form.get('terms'),
            'footer': request.form.get('footer'),
            'payment_instructions': request.form.get('payment_instructions'),
            'created_by_id': session.get('user_id'),
            'status': 'Draft'
        }
        
        # Create the invoice
        invoice_id = create_invoice(invoice_data)
        
        flash('Invoice created successfully. Now you can add line items.', 'success')
        return redirect(url_for('invoices.edit_invoice', invoice_id=invoice_id))
    
    # GET request - show the create form
    clients = get_all_clients()
    projects = get_all_projects()
    
    # Set default dates
    today = datetime.now().date()
    due_date = today + timedelta(days=30)
    
    return render_template(
        'invoices/create.html', 
        clients=clients,
        projects=projects,
        today=today.strftime('%Y-%m-%d'),
        due_date=due_date.strftime('%Y-%m-%d')
    )

@bp.route('/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    """View an invoice"""
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    # Get invoice items
    items = get_invoice_items(invoice_id)
    
    # Get payment history
    payments = get_invoice_payments(invoice_id)
    
    return render_template(
        'invoices/detail.html', 
        invoice=invoice, 
        items=items,
        payments=payments
    )

@bp.route('/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_invoice(invoice_id):
    """Edit an existing invoice"""
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    # Only draft invoices can be edited
    if invoice['status'] != 'Draft':
        flash('Only draft invoices can be edited', 'error')
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))
    
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        project_id = request.form.get('project_id', None) or None  # Convert empty string to None
        
        if not client_id:
            flash('Client is required', 'error')
            return redirect(url_for('invoices.edit_invoice', invoice_id=invoice_id))
        
        # Gather invoice data from form
        invoice_data = {
            'client_id': client_id,
            'project_id': project_id,
            'issue_date': request.form.get('issue_date'),
            'due_date': request.form.get('due_date'),
            'tax_rate': request.form.get('tax_rate', 0),
            'discount_amount': request.form.get('discount_amount', 0),
            'notes': request.form.get('notes'),
            'terms': request.form.get('terms'),
            'footer': request.form.get('footer'),
            'payment_instructions': request.form.get('payment_instructions')
        }
        
        # Update the invoice
        update_invoice(invoice_id, invoice_data)
        
        flash('Invoice updated successfully', 'success')
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))
    
    # GET request - show the edit form
    clients = get_all_clients()
    projects = get_all_projects()
    items = get_invoice_items(invoice_id)
    
    return render_template(
        'invoices/edit.html', 
        invoice=invoice, 
        clients=clients,
        projects=projects,
        items=items
    )

@bp.route('/<int:invoice_id>/delete', methods=['POST'])
@login_required
def delete_invoice_route(invoice_id):
    """Delete an invoice"""
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    # Only draft invoices can be deleted
    if invoice['status'] != 'Draft':
        flash('Only draft invoices can be deleted', 'error')
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))
    
    # Delete the invoice
    success = delete_invoice(invoice_id)
    
    if success:
        flash('Invoice deleted successfully', 'success')
    else:
        flash('Failed to delete invoice', 'error')
        
    return redirect(url_for('invoices.list_invoices'))

@bp.route('/<int:invoice_id>/items', methods=['GET', 'POST'])
@login_required
def manage_invoice_items(invoice_id):
    """Manage invoice items (line items)"""
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    # Only draft invoices can have items added/edited
    if invoice['status'] != 'Draft':
        flash('Only draft invoices can be modified', 'error')
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))
    
    if request.method == 'POST':
        # Process form data for adding or updating items
        if 'item_data' in request.form:
            # Parse JSON data from form
            try:
                items_data = json.loads(request.form['item_data'])
                
                # Update invoice with new items
                update_invoice(invoice_id, {}, items_data)
                
                return jsonify({'success': True, 'message': 'Items updated successfully'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error updating items: {str(e)}'})
        else:
            flash('No item data received', 'error')
            return redirect(url_for('invoices.manage_invoice_items', invoice_id=invoice_id))
    
    # GET request - show the items management page
    items = get_invoice_items(invoice_id)
    
    return render_template(
        'invoices/items.html', 
        invoice=invoice, 
        items=items
    )

@bp.route('/<int:invoice_id>/send', methods=['POST'])
@login_required
def send_invoice(invoice_id):
    """Mark invoice as sent and optionally send email"""
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    # Only draft invoices can be sent
    if invoice['status'] != 'Draft':
        flash('This invoice has already been sent', 'error')
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))
    
    # Check if we should send email
    send_email = request.form.get('send_email') == 'yes'
    
    if send_email:
        # Try to send email
        success = send_invoice_email(invoice_id, 'new')
        if success:
            flash('Invoice sent successfully via email', 'success')
        else:
            # Just mark as sent if email fails
            mark_invoice_as_sent(invoice_id)
            flash('Failed to send email, but invoice marked as sent', 'warning')
    else:
        # Just mark as sent without sending email
        mark_invoice_as_sent(invoice_id)
        flash('Invoice marked as sent', 'success')
    
    return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))

@bp.route('/<int:invoice_id>/cancel', methods=['POST'])
@login_required
def cancel_invoice(invoice_id):
    """Cancel an invoice"""
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    # Can't cancel already paid invoices
    if invoice['status'] in ['Paid', 'Cancelled']:
        flash('Cannot cancel this invoice', 'error')
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))
    
    reason = request.form.get('reason')
    success = mark_invoice_as_cancelled(invoice_id, reason)
    
    if success:
        flash('Invoice cancelled successfully', 'success')
    else:
        flash('Failed to cancel invoice', 'error')
        
    return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))

@bp.route('/<int:invoice_id>/payment', methods=['GET', 'POST'])
@login_required
def record_payment_route(invoice_id):
    """Record a payment for an invoice"""
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    if request.method == 'POST':
        amount = request.form.get('amount', 0)
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            flash('Invalid payment amount', 'error')
            return redirect(url_for('invoices.record_payment_route', invoice_id=invoice_id))
        
        payment_data = {
            'invoice_id': invoice_id,
            'amount': amount,
            'payment_date': request.form.get('payment_date', datetime.now().strftime('%Y-%m-%d')),
            'payment_method': request.form.get('payment_method', Payment.METHOD_CHECK),
            'reference_number': request.form.get('reference_number'),
            'notes': request.form.get('notes'),
            'created_by_id': session.get('user_id')
        }
        
        # Record the payment
        payment_id = record_payment(payment_data)
        
        if payment_id:
            # Check if we should send receipt
            send_receipt = request.form.get('send_receipt') == 'yes'
            
            if send_receipt:
                # Try to send receipt email
                success = send_invoice_email(invoice_id, 'receipt')
                if success:
                    flash('Payment recorded and receipt sent', 'success')
                else:
                    flash('Payment recorded but failed to send receipt', 'warning')
            else:
                flash('Payment recorded successfully', 'success')
        else:
            flash('Failed to record payment', 'error')
            
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))
    
    # GET request - show payment form
    return render_template(
        'invoices/payment.html', 
        invoice=invoice
    )

@bp.route('/<int:invoice_id>/payment/<int:payment_id>/delete', methods=['POST'])
@login_required
def delete_payment_route(invoice_id, payment_id):
    """Delete a payment"""
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    success = delete_payment(payment_id)
    
    if success:
        flash('Payment deleted successfully', 'success')
    else:
        flash('Failed to delete payment', 'error')
        
    return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))

@bp.route('/<int:invoice_id>/print')
@login_required
def print_invoice(invoice_id):
    """Show printable version of invoice"""
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    # Get invoice items
    items = get_invoice_items(invoice_id)
    
    # Get company info
    company_info = {
        'name': 'AKC LLC Construction',
        'address': '123 Construction Way',
        'city': 'Anytown',
        'state': 'NY',
        'zip': '12345',
        'phone': '(555) 123-4567',
        'email': 'info@akcllcconstruction.com',
        'website': 'www.akcllcconstruction.com',
        'logo_url': url_for('static', filename='img/akc-logo.jpg')
    }
    
    return render_template(
        'invoices/print.html', 
        invoice=invoice, 
        items=items,
        company=company_info,
        print_mode=True
    )

@bp.route('/dashboard')
@login_required
def invoice_dashboard():
    """Dashboard showing invoice statistics"""
    # Get overdue invoices
    overdue_invoices = get_overdue_invoices()
    
    # Get upcoming invoices (due in next 7 days)
    upcoming_invoices = get_upcoming_invoices(7)
    
    # Get invoice counts by status
    invoices_by_status = get_all_invoices(limit=1000)  # We'll do the grouping here
    
    # Group and count invoices by status
    status_counts = {}
    for invoice in invoices_by_status:
        status = invoice['status']
        if status not in status_counts:
            status_counts[status] = {'count': 0, 'total': 0}
        status_counts[status]['count'] += 1
        status_counts[status]['total'] += invoice['total_amount']
    
    return render_template(
        'invoices/dashboard.html',
        overdue_invoices=overdue_invoices,
        upcoming_invoices=upcoming_invoices,
        status_counts=status_counts
    )

@bp.route('/client/<int:client_id>')
@login_required
def client_invoices(client_id):
    """List invoices for a specific client"""
    client = get_client_by_id(client_id)
    if not client:
        flash('Client not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    invoices = get_all_invoices(client_id=client_id)
    
    return render_template(
        'invoices/client_invoices.html', 
        invoices=invoices, 
        client=client
    )

@bp.route('/project/<int:project_id>')
@login_required
def project_invoices(project_id):
    """List invoices for a specific project"""
    project = get_project_by_id(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('invoices.list_invoices'))
    
    invoices = get_all_invoices(project_id=project_id)
    
    return render_template(
        'invoices/project_invoices.html', 
        invoices=invoices, 
        project=project
    )

@bp.route('/api/items/<int:invoice_id>')
@login_required
def api_get_invoice_items(invoice_id):
    """API endpoint to get invoice items as JSON"""
    items = get_invoice_items(invoice_id)
    return jsonify(items) 