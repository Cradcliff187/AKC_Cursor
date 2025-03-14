"""
Invoice management service functions.
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from flask import current_app, g
from werkzeug.utils import secure_filename
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.payment import Payment
import uuid
from app.services.supabase import supabase

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Invoice CRUD Operations
def get_all_invoices(limit=50, offset=0, status=None, client_id=None, project_id=None, date_from=None, date_to=None):
    """Get all invoices with optional filtering"""
    conn = get_db_connection()
    query = """
        SELECT i.*, c.name as client_name, p.name as project_name, u.name as created_by_name
        FROM invoices i 
        LEFT JOIN clients c ON i.client_id = c.id
        LEFT JOIN projects p ON i.project_id = p.id
        LEFT JOIN users u ON i.created_by_id = u.id
    """
    params = []
    
    # Add filters if provided
    filters = []
    if status:
        filters.append("i.status = ?")
        params.append(status)
    
    if client_id:
        filters.append("i.client_id = ?")
        params.append(client_id)
        
    if project_id:
        filters.append("i.project_id = ?")
        params.append(project_id)
        
    if date_from:
        filters.append("i.issue_date >= ?")
        params.append(date_from)
        
    if date_to:
        filters.append("i.issue_date <= ?")
        params.append(date_to)
    
    if filters:
        query += " WHERE " + " AND ".join(filters)
    
    query += " ORDER BY i.issue_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    invoices = conn.execute(query, params).fetchall()
    conn.close()
    
    return [dict(invoice) for invoice in invoices]

def get_invoice_by_id(invoice_id):
    """Get an invoice by its ID"""
    conn = get_db_connection()
    invoice = conn.execute(
        """SELECT i.*, c.name as client_name, c.email as client_email, c.address as client_address,
                  c.phone as client_phone, p.name as project_name, u.name as created_by_name 
           FROM invoices i 
           LEFT JOIN clients c ON i.client_id = c.id
           LEFT JOIN projects p ON i.project_id = p.id
           LEFT JOIN users u ON i.created_by_id = u.id
           WHERE i.id = ?""", 
        (invoice_id,)
    ).fetchone()
    conn.close()
    
    if invoice:
        return dict(invoice)
    return None

def get_next_invoice_number():
    """Generate the next available invoice number"""
    conn = get_db_connection()
    result = conn.execute("SELECT COUNT(*) as count FROM invoices").fetchone()
    count = result['count'] + 1
    
    # Format: INV-YYYYMMDD-XXXX where XXXX is a sequential number
    today = datetime.now().strftime('%Y%m%d')
    invoice_number = f"INV-{today}-{count:04d}"
    
    # Check if this invoice number already exists
    existing = conn.execute("SELECT id FROM invoices WHERE invoice_number = ?", (invoice_number,)).fetchone()
    
    if existing:
        # If it exists, append a random string
        random_str = str(uuid.uuid4())[:4]
        invoice_number = f"INV-{today}-{count:04d}-{random_str}"
    
    conn.close()
    return invoice_number

def create_invoice(invoice_data, items_data=None):
    """Create a new invoice"""
    conn = get_db_connection()
    
    # Generate invoice number if not provided
    if not invoice_data.get('invoice_number'):
        invoice_data['invoice_number'] = get_next_invoice_number()
    
    # Set default terms if not provided
    if not invoice_data.get('terms'):
        invoice_data['terms'] = "Payment due within 30 days of invoice date."
    
    # Calculate due date if not provided
    if not invoice_data.get('due_date'):
        issue_date = invoice_data.get('issue_date', datetime.now().strftime('%Y-%m-%d'))
        if isinstance(issue_date, str):
            issue_date = datetime.strptime(issue_date, '%Y-%m-%d').date()
        elif not isinstance(issue_date, datetime):
            issue_date = datetime.now().date()
        
        invoice_data['due_date'] = (issue_date + timedelta(days=30)).strftime('%Y-%m-%d')
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO invoices (
            invoice_number, client_id, project_id, status, issue_date, due_date,
            subtotal, tax_rate, tax_amount, discount_amount, total_amount,
            amount_paid, balance_due, notes, terms, footer, payment_instructions,
            created_by_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        invoice_data.get('invoice_number'),
        invoice_data.get('client_id'),
        invoice_data.get('project_id'),
        invoice_data.get('status', 'Draft'),
        invoice_data.get('issue_date', datetime.now().strftime('%Y-%m-%d')),
        invoice_data.get('due_date'),
        invoice_data.get('subtotal', 0),
        invoice_data.get('tax_rate', 0),
        invoice_data.get('tax_amount', 0),
        invoice_data.get('discount_amount', 0),
        invoice_data.get('total_amount', 0),
        invoice_data.get('amount_paid', 0),
        invoice_data.get('balance_due', 0),
        invoice_data.get('notes'),
        invoice_data.get('terms'),
        invoice_data.get('footer'),
        invoice_data.get('payment_instructions'),
        invoice_data.get('created_by_id'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    invoice_id = cursor.lastrowid
    
    # Save invoice items if provided
    if items_data:
        for item in items_data:
            item['invoice_id'] = invoice_id
            save_invoice_item(conn, item)
    
    # Recalculate totals
    recalculate_invoice_totals(conn, invoice_id)
    
    conn.commit()
    conn.close()
    
    return invoice_id

def update_invoice(invoice_id, invoice_data, items_data=None):
    """Update an existing invoice"""
    conn = get_db_connection()
    
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE invoices SET
            client_id = COALESCE(?, client_id),
            project_id = ?,
            status = COALESCE(?, status),
            issue_date = COALESCE(?, issue_date),
            due_date = COALESCE(?, due_date),
            tax_rate = COALESCE(?, tax_rate),
            discount_amount = COALESCE(?, discount_amount),
            notes = ?,
            terms = ?,
            footer = ?,
            payment_instructions = ?,
            updated_at = ?
        WHERE id = ?
    ''', (
        invoice_data.get('client_id'),
        invoice_data.get('project_id'),
        invoice_data.get('status'),
        invoice_data.get('issue_date'),
        invoice_data.get('due_date'),
        invoice_data.get('tax_rate'),
        invoice_data.get('discount_amount'),
        invoice_data.get('notes'),
        invoice_data.get('terms'),
        invoice_data.get('footer'),
        invoice_data.get('payment_instructions'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        invoice_id
    ))
    
    # Update or add items if provided
    if items_data is not None:
        # Delete existing items
        cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        
        # Save new items
        for item in items_data:
            item['invoice_id'] = invoice_id
            save_invoice_item(conn, item)
    
    # Recalculate totals
    recalculate_invoice_totals(conn, invoice_id)
    
    conn.commit()
    
    # Get the updated invoice
    updated_invoice = get_invoice_by_id(invoice_id)
    
    conn.close()
    
    return updated_invoice

def delete_invoice(invoice_id):
    """Delete an invoice and its items"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if invoice exists
    invoice = cursor.execute("SELECT id, status FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    if not invoice:
        conn.close()
        return False
    
    # Only allow deletion of draft invoices
    if invoice['status'] != 'Draft':
        conn.close()
        return False
    
    # Delete items first (foreign key CASCADE should handle this automatically)
    cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
    
    # Delete payments
    cursor.execute("DELETE FROM payments WHERE invoice_id = ?", (invoice_id,))
    
    # Delete invoice
    cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
    
    conn.commit()
    conn.close()
    
    return True

# Invoice Item Operations
def get_invoice_items(invoice_id):
    """Get all items for a specific invoice"""
    conn = get_db_connection()
    items = conn.execute(
        "SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY sort_order ASC", 
        (invoice_id,)
    ).fetchall()
    conn.close()
    
    return [dict(item) for item in items]

def save_invoice_item(conn, item_data):
    """Save an invoice item (helper function)"""
    cursor = conn.cursor()
    
    # Calculate amount if not provided
    amount = item_data.get('amount')
    if not amount:
        quantity = float(item_data.get('quantity', 1))
        unit_price = float(item_data.get('unit_price', 0))
        amount = quantity * unit_price
    
    cursor.execute('''
        INSERT INTO invoice_items (
            invoice_id, description, quantity, unit_price, amount,
            type, sort_order, taxable, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        item_data.get('invoice_id'),
        item_data.get('description', ''),
        item_data.get('quantity', 1),
        item_data.get('unit_price', 0),
        amount,
        item_data.get('type', 'Service'),
        item_data.get('sort_order', 0),
        item_data.get('taxable', True),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    return cursor.lastrowid

def recalculate_invoice_totals(conn, invoice_id):
    """Recalculate invoice totals based on items"""
    cursor = conn.cursor()
    
    # Get all items
    items = cursor.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,)).fetchall()
    
    # Calculate subtotal
    subtotal = sum(item['amount'] for item in items)
    
    # Get tax rate
    invoice = cursor.execute("SELECT tax_rate, discount_amount, amount_paid FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    tax_rate = invoice['tax_rate']
    discount_amount = invoice['discount_amount']
    amount_paid = invoice['amount_paid']
    
    # Calculate tax
    taxable_items = [item for item in items if item['taxable']]
    taxable_amount = sum(item['amount'] for item in taxable_items)
    tax_amount = taxable_amount * (tax_rate / 100) if tax_rate else 0
    
    # Calculate total and balance
    total_amount = subtotal + tax_amount - discount_amount
    balance_due = total_amount - amount_paid
    
    # Determine status based on payment
    status = cursor.execute("SELECT status FROM invoices WHERE id = ?", (invoice_id,)).fetchone()['status']
    
    # Only update status if not draft
    if status != 'Draft':
        if balance_due <= 0:
            status = 'Paid'
            # Set paid date if fully paid
            cursor.execute("UPDATE invoices SET paid_date = ? WHERE id = ? AND paid_date IS NULL", 
                          (datetime.now().strftime('%Y-%m-%d'), invoice_id))
        elif amount_paid > 0:
            status = 'Partially Paid'
        elif datetime.now().date() > datetime.strptime(invoice['due_date'], '%Y-%m-%d').date():
            status = 'Overdue'
    
    # Update invoice with calculated values
    cursor.execute('''
        UPDATE invoices SET
            subtotal = ?,
            tax_amount = ?,
            total_amount = ?,
            balance_due = ?,
            status = ?,
            updated_at = ?
        WHERE id = ?
    ''', (
        subtotal,
        tax_amount,
        total_amount,
        balance_due,
        status,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        invoice_id
    ))
    
    return {
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
        'balance_due': balance_due,
        'status': status
    }

# Payment Operations
def get_invoice_payments(invoice_id):
    """Get all payments for a specific invoice"""
    conn = get_db_connection()
    payments = conn.execute(
        """SELECT p.*, u.name as created_by_name
           FROM payments p
           LEFT JOIN users u ON p.created_by_id = u.id
           WHERE p.invoice_id = ?
           ORDER BY p.payment_date DESC""",
        (invoice_id,)
    ).fetchall()
    conn.close()
    
    return [dict(payment) for payment in payments]

def record_payment(payment_data):
    """Record a payment for an invoice"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert the payment
    cursor.execute('''
        INSERT INTO payments (
            invoice_id, amount, payment_date, payment_method,
            reference_number, notes, created_by_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        payment_data.get('invoice_id'),
        payment_data.get('amount', 0),
        payment_data.get('payment_date', datetime.now().strftime('%Y-%m-%d')),
        payment_data.get('payment_method', 'Check'),
        payment_data.get('reference_number'),
        payment_data.get('notes'),
        payment_data.get('created_by_id'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    payment_id = cursor.lastrowid
    
    # Update invoice amount_paid
    invoice_id = payment_data.get('invoice_id')
    amount = float(payment_data.get('amount', 0))
    
    # Get current amount paid
    current_amount_paid = cursor.execute(
        "SELECT amount_paid FROM invoices WHERE id = ?", (invoice_id,)
    ).fetchone()['amount_paid']
    
    new_amount_paid = current_amount_paid + amount
    
    # Update invoice with new payment amount
    cursor.execute(
        "UPDATE invoices SET amount_paid = ?, updated_at = ? WHERE id = ?",
        (new_amount_paid, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), invoice_id)
    )
    
    # Recalculate totals
    recalculate_invoice_totals(conn, invoice_id)
    
    conn.commit()
    conn.close()
    
    return payment_id

def delete_payment(payment_id):
    """Delete a payment and update invoice totals"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get payment details before deletion
    payment = cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()
    if not payment:
        conn.close()
        return False
    
    invoice_id = payment['invoice_id']
    amount = payment['amount']
    
    # Get current amount paid
    current_amount_paid = cursor.execute(
        "SELECT amount_paid FROM invoices WHERE id = ?", (invoice_id,)
    ).fetchone()['amount_paid']
    
    new_amount_paid = max(0, current_amount_paid - amount)
    
    # Update invoice with new payment amount
    cursor.execute(
        "UPDATE invoices SET amount_paid = ?, updated_at = ? WHERE id = ?",
        (new_amount_paid, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), invoice_id)
    )
    
    # Delete the payment
    cursor.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
    
    # Recalculate totals
    recalculate_invoice_totals(conn, invoice_id)
    
    conn.commit()
    conn.close()
    
    return True

# Invoice Status Operations
def mark_invoice_as_sent(invoice_id):
    """Mark an invoice as sent"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update status and sent date
    cursor.execute(
        "UPDATE invoices SET status = ?, sent_date = ?, updated_at = ? WHERE id = ? AND status = 'Draft'",
        ('Sent', datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), invoice_id)
    )
    
    affected_rows = cursor.rowcount
    conn.commit()
    conn.close()
    
    return affected_rows > 0

def mark_invoice_as_viewed(invoice_id):
    """Mark an invoice as viewed by client"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update status only if current status is 'Sent'
    cursor.execute(
        "UPDATE invoices SET status = ?, updated_at = ? WHERE id = ? AND status = 'Sent'",
        ('Viewed', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), invoice_id)
    )
    
    affected_rows = cursor.rowcount
    conn.commit()
    conn.close()
    
    return affected_rows > 0

def mark_invoice_as_cancelled(invoice_id, reason=None):
    """Cancel an invoice"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update status and add reason to notes
    if reason:
        cursor.execute(
            "UPDATE invoices SET status = ?, notes = CASE WHEN notes IS NULL THEN ? ELSE notes || '\n\n' || ? END, updated_at = ? WHERE id = ?",
            ('Cancelled', f"Cancellation reason: {reason}", f"Cancellation reason: {reason}", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), invoice_id)
        )
    else:
        cursor.execute(
            "UPDATE invoices SET status = ?, updated_at = ? WHERE id = ?",
            ('Cancelled', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), invoice_id)
        )
    
    affected_rows = cursor.rowcount
    conn.commit()
    conn.close()
    
    return affected_rows > 0

# Reporting Functions
def get_invoices_by_status():
    """Get count and total amount of invoices grouped by status"""
    conn = get_db_connection()
    results = conn.execute('''
        SELECT status, COUNT(*) as count, SUM(total_amount) as total
        FROM invoices
        GROUP BY status
    ''').fetchall()
    conn.close()
    
    return [dict(row) for row in results]

def get_overdue_invoices():
    """Get all overdue invoices"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    invoices = conn.execute('''
        SELECT i.*, c.name as client_name, c.email as client_email
        FROM invoices i
        LEFT JOIN clients c ON i.client_id = c.id
        WHERE i.due_date < ? AND i.balance_due > 0 AND i.status != 'Cancelled'
        ORDER BY i.due_date ASC
    ''', (today,)).fetchall()
    conn.close()
    
    return [dict(invoice) for invoice in invoices]

def get_upcoming_invoices(days=7):
    """Get invoices due in the next X days"""
    today = datetime.now().strftime('%Y-%m-%d')
    future_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    invoices = conn.execute('''
        SELECT i.*, c.name as client_name, c.email as client_email
        FROM invoices i
        LEFT JOIN clients c ON i.client_id = c.id
        WHERE i.due_date BETWEEN ? AND ? AND i.balance_due > 0 AND i.status != 'Cancelled'
        ORDER BY i.due_date ASC
    ''', (today, future_date)).fetchall()
    conn.close()
    
    return [dict(invoice) for invoice in invoices]

def get_monthly_revenue(year=None, month=None):
    """Get revenue data by month"""
    if not year:
        year = datetime.now().year
    
    conn = get_db_connection()
    
    if month:
        # Get data for specific month
        start_date = f"{year}-{month:02d}-01"
        
        # Calculate end date (last day of month)
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
            
        results = conn.execute('''
            SELECT SUM(amount) as total, payment_method
            FROM payments
            WHERE payment_date >= ? AND payment_date < ?
            GROUP BY payment_method
        ''', (start_date, end_date)).fetchall()
    else:
        # Get data for entire year by month
        results = conn.execute('''
            SELECT 
                strftime('%m', payment_date) as month,
                SUM(amount) as total
            FROM payments
            WHERE strftime('%Y', payment_date) = ?
            GROUP BY month
            ORDER BY month
        ''', (str(year),)).fetchall()
    
    conn.close()
    
    return [dict(row) for row in results]

# Email Functions
def send_invoice_email(invoice_id, email_type='new'):
    """Send invoice email to client"""
    from app.services.email import send_invoice_email as send_email
    
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        return False
        
    # Get items
    items = get_invoice_items(invoice_id)
    
    # Determine email type and subject
    if email_type == 'new':
        subject = f"Invoice #{invoice['invoice_number']} from AKC LLC Construction"
        template = 'invoice_new'
    elif email_type == 'reminder':
        days_overdue = (datetime.now().date() - datetime.strptime(invoice['due_date'], '%Y-%m-%d').date()).days
        subject = f"Reminder: Invoice #{invoice['invoice_number']} is {days_overdue} days overdue"
        template = 'invoice_reminder'
    elif email_type == 'receipt':
        subject = f"Payment Receipt for Invoice #{invoice['invoice_number']}"
        template = 'invoice_receipt'
    else:
        subject = f"Invoice #{invoice['invoice_number']} from AKC LLC Construction"
        template = 'invoice_generic'
    
    # Send email
    result = send_email(
        invoice['client_email'],
        subject,
        template,
        {
            'invoice': invoice,
            'invoice_items': items,
            'client': {
                'name': invoice['client_name'],
                'email': invoice['client_email'],
                'address': invoice['client_address'],
                'phone': invoice['client_phone']
            }
        }
    )
    
    # If email sent successfully, update invoice
    if result and email_type == 'new':
        mark_invoice_as_sent(invoice_id)
    elif result and email_type == 'reminder':
        conn = get_db_connection()
        conn.execute(
            "UPDATE invoices SET last_reminder_date = ?, updated_at = ? WHERE id = ?",
            (datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), invoice_id)
        )
        conn.commit()
        conn.close()
    
    return result

def get_invoices():
    try:
        response = supabase.table('invoices').select('*').execute()
        return response.data
    except Exception as e:
        current_app.logger.error(f"Error fetching invoices: {str(e)}")
        return []

def get_invoice(invoice_id):
    try:
        response = supabase.table('invoices').select('*').eq('id', invoice_id).single().execute()
        return response.data
    except Exception as e:
        current_app.logger.error(f"Error fetching invoice {invoice_id}: {str(e)}")
        return None

def create_invoice(data):
    try:
        data['created_at'] = datetime.utcnow().isoformat()
        data['updated_at'] = datetime.utcnow().isoformat()
        response = supabase.table('invoices').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        current_app.logger.error(f"Error creating invoice: {str(e)}")
        return None

def update_invoice(invoice_id, data):
    try:
        data['updated_at'] = datetime.utcnow().isoformat()
        response = supabase.table('invoices').update(data).eq('id', invoice_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        current_app.logger.error(f"Error updating invoice {invoice_id}: {str(e)}")
        return None

def delete_invoice(invoice_id):
    try:
        response = supabase.table('invoices').delete().eq('id', invoice_id).execute()
        return True
    except Exception as e:
        current_app.logger.error(f"Error deleting invoice {invoice_id}: {str(e)}")
        return False 