"""
Bid and proposal management service functions.
"""
import sqlite3
import os
import json
from datetime import datetime
from flask import current_app, g
from werkzeug.utils import secure_filename
from app.models.bid import Bid
from app.models.bid_item import BidItem
import uuid

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_all_bids(limit=50, offset=0, status=None, client_id=None):
    """Get all bids with optional filtering"""
    conn = get_db_connection()
    query = "SELECT b.*, c.name as client_name FROM bids b LEFT JOIN clients c ON b.client_id = c.id"
    params = []
    
    # Add filters if provided
    filters = []
    if status:
        filters.append("b.status = ?")
        params.append(status)
    
    if client_id:
        filters.append("b.client_id = ?")
        params.append(client_id)
    
    if filters:
        query += " WHERE " + " AND ".join(filters)
    
    query += " ORDER BY b.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    bids = conn.execute(query, params).fetchall()
    conn.close()
    
    return [dict(bid) for bid in bids]

def get_bid_by_id(bid_id):
    """Get a bid by its ID"""
    conn = get_db_connection()
    bid = conn.execute(
        """SELECT b.*, c.name as client_name, p.name as project_name, u.name as created_by_name 
           FROM bids b 
           LEFT JOIN clients c ON b.client_id = c.id
           LEFT JOIN projects p ON b.project_id = p.id
           LEFT JOIN users u ON b.created_by_id = u.id
           WHERE b.id = ?""", 
        (bid_id,)
    ).fetchone()
    conn.close()
    
    if bid:
        return dict(bid)
    return None

def get_bid_items(bid_id):
    """Get all items for a specific bid"""
    conn = get_db_connection()
    items = conn.execute(
        "SELECT * FROM bid_items WHERE bid_id = ? ORDER BY sort_order ASC", 
        (bid_id,)
    ).fetchall()
    conn.close()
    
    return [dict(item) for item in items]

def create_bid(bid_data, items_data=None):
    """Create a new bid"""
    conn = get_db_connection()
    
    # Create bid number if not provided
    if not bid_data.get('bid_number'):
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        random_str = str(uuid.uuid4())[:8]
        bid_data['bid_number'] = f"BID-{timestamp}-{random_str}"
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bids (
            name, client_id, project_id, created_by_id, status, version,
            bid_number, proposal_date, valid_until, total_amount,
            labor_cost, material_cost, overhead_cost, profit_margin,
            description, notes, terms_and_conditions, client_message,
            file_path, original_filename, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        bid_data.get('name'),
        bid_data.get('client_id'),
        bid_data.get('project_id'),
        bid_data.get('created_by_id'),
        bid_data.get('status', 'Draft'),
        bid_data.get('version', 1),
        bid_data.get('bid_number'),
        bid_data.get('proposal_date', datetime.now().strftime('%Y-%m-%d')),
        bid_data.get('valid_until'),
        bid_data.get('total_amount', 0),
        bid_data.get('labor_cost', 0),
        bid_data.get('material_cost', 0),
        bid_data.get('overhead_cost', 0),
        bid_data.get('profit_margin', 0),
        bid_data.get('description'),
        bid_data.get('notes'),
        bid_data.get('terms_and_conditions'),
        bid_data.get('client_message'),
        bid_data.get('file_path'),
        bid_data.get('original_filename'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    bid_id = cursor.lastrowid
    
    # Save bid items if provided
    if items_data:
        for item in items_data:
            item['bid_id'] = bid_id
            _save_bid_item(conn, item)
    
    # Save initial version
    bid = get_bid_by_id(bid_id)
    _save_bid_version(conn, bid_id, 1, bid, bid_data.get('created_by_id'))
    
    conn.commit()
    conn.close()
    
    return bid_id

def update_bid(bid_id, bid_data, items_data=None):
    """Update an existing bid"""
    conn = get_db_connection()
    
    # Get current version
    current_version = conn.execute("SELECT version FROM bids WHERE id = ?", (bid_id,)).fetchone()
    new_version = current_version[0] + 1 if current_version else 1
    
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE bids SET
            name = ?, client_id = ?, project_id = ?, status = ?, version = ?,
            bid_number = ?, proposal_date = ?, valid_until = ?, total_amount = ?,
            labor_cost = ?, material_cost = ?, overhead_cost = ?, profit_margin = ?,
            description = ?, notes = ?, terms_and_conditions = ?, client_message = ?,
            client_response = ?, client_response_date = ?,
            file_path = COALESCE(?, file_path), 
            original_filename = COALESCE(?, original_filename),
            updated_at = ?
        WHERE id = ?
    ''', (
        bid_data.get('name'),
        bid_data.get('client_id'),
        bid_data.get('project_id'),
        bid_data.get('status'),
        new_version,
        bid_data.get('bid_number'),
        bid_data.get('proposal_date'),
        bid_data.get('valid_until'),
        bid_data.get('total_amount'),
        bid_data.get('labor_cost'),
        bid_data.get('material_cost'),
        bid_data.get('overhead_cost'),
        bid_data.get('profit_margin'),
        bid_data.get('description'),
        bid_data.get('notes'),
        bid_data.get('terms_and_conditions'),
        bid_data.get('client_message'),
        bid_data.get('client_response'),
        bid_data.get('client_response_date'),
        bid_data.get('file_path'),
        bid_data.get('original_filename'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        bid_id
    ))
    
    # Update bid items if provided
    if items_data is not None:
        # Delete existing items
        cursor.execute("DELETE FROM bid_items WHERE bid_id = ?", (bid_id,))
        
        # Save new items
        for item in items_data:
            item['bid_id'] = bid_id
            _save_bid_item(conn, item)
    
    # Save new version
    updated_bid = get_bid_by_id(bid_id)
    _save_bid_version(conn, bid_id, new_version, updated_bid, bid_data.get('created_by_id'))
    
    conn.commit()
    conn.close()
    
    return updated_bid

def delete_bid(bid_id):
    """Delete a bid and its items"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete items first (foreign key constraint will handle this automatically)
    cursor.execute("DELETE FROM bid_items WHERE bid_id = ?", (bid_id,))
    
    # Delete versions
    cursor.execute("DELETE FROM bid_versions WHERE bid_id = ?", (bid_id,))
    
    # Delete bid
    cursor.execute("DELETE FROM bids WHERE id = ?", (bid_id,))
    
    conn.commit()
    conn.close()
    
    return True

def _save_bid_item(conn, item_data):
    """Save a bid item (helper function)"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bid_items (
            bid_id, item_type, category, description, quantity, unit, 
            unit_cost, total_cost, markup_percentage, markup_amount, 
            total_price, notes, sort_order
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        item_data.get('bid_id'),
        item_data.get('item_type', 'Labor'),
        item_data.get('category'),
        item_data.get('description', ''),
        item_data.get('quantity', 1),
        item_data.get('unit', 'Hours'),
        item_data.get('unit_cost', 0),
        item_data.get('total_cost', 0),
        item_data.get('markup_percentage', 0),
        item_data.get('markup_amount', 0),
        item_data.get('total_price', 0),
        item_data.get('notes'),
        item_data.get('sort_order', 0)
    ))
    
    return cursor.lastrowid

def _save_bid_version(conn, bid_id, version_number, bid_data, created_by_id):
    """Save a version of a bid (helper function)"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bid_versions (
            bid_id, version_number, data, created_by_id, created_at
        ) VALUES (?, ?, ?, ?, ?)
    ''', (
        bid_id,
        version_number,
        json.dumps(bid_data),
        created_by_id,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    return cursor.lastrowid

def get_bid_versions(bid_id):
    """Get all versions of a bid"""
    conn = get_db_connection()
    versions = conn.execute(
        """SELECT bv.*, u.name as created_by_name
           FROM bid_versions bv
           LEFT JOIN users u ON bv.created_by_id = u.id
           WHERE bv.bid_id = ? 
           ORDER BY bv.version_number DESC""", 
        (bid_id,)
    ).fetchall()
    conn.close()
    
    return [dict(version) for version in versions]

def get_bid_version_data(bid_id, version_number):
    """Get a specific version of a bid"""
    conn = get_db_connection()
    version = conn.execute(
        "SELECT * FROM bid_versions WHERE bid_id = ? AND version_number = ?", 
        (bid_id, version_number)
    ).fetchone()
    conn.close()
    
    if version:
        version_dict = dict(version)
        version_dict['data'] = json.loads(version_dict['data'])
        return version_dict
    return None

def calculate_bid_totals(bid_id):
    """Recalculate bid totals based on items"""
    conn = get_db_connection()
    items = get_bid_items(bid_id)
    
    labor_cost = 0
    material_cost = 0
    other_cost = 0
    
    for item in items:
        if item['item_type'] == 'Labor':
            labor_cost += item['total_price']
        elif item['item_type'] == 'Material':
            material_cost += item['total_price']
        else:
            other_cost += item['total_price']
    
    total_amount = labor_cost + material_cost + other_cost
    
    # Update bid with calculated values
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE bids SET
            labor_cost = ?,
            material_cost = ?,
            overhead_cost = ?,
            total_amount = ?,
            updated_at = ?
        WHERE id = ?
    ''', (
        labor_cost,
        material_cost,
        other_cost,
        total_amount,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        bid_id
    ))
    
    conn.commit()
    conn.close()
    
    return {
        'labor_cost': labor_cost,
        'material_cost': material_cost,
        'overhead_cost': other_cost,
        'total_amount': total_amount
    }

def save_bid_document(bid_id, file):
    """Save a document (PDF, etc.) associated with a bid"""
    if not file:
        return None
    
    filename = secure_filename(file.filename)
    base_path = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    bids_path = os.path.join(base_path, 'Bids')
    
    # Create directory if it doesn't exist
    os.makedirs(bids_path, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    file_path = os.path.join(bids_path, unique_filename)
    
    # Save the file
    file.save(file_path)
    
    # Update the bid record with the file path
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bids SET file_path = ?, original_filename = ? WHERE id = ?",
        (file_path, filename, bid_id)
    )
    conn.commit()
    conn.close()
    
    return {
        'file_path': file_path,
        'original_filename': filename
    }

def convert_bid_to_project(bid_id, project_data=None):
    """Convert an accepted bid to a project"""
    bid = get_bid_by_id(bid_id)
    if not bid:
        return None
    
    # Only convert accepted bids
    if bid['status'] != 'Accepted':
        return {
            'success': False,
            'message': 'Only accepted bids can be converted to projects'
        }
    
    # Check if already converted
    if bid['project_id']:
        return {
            'success': False,
            'message': 'Bid already converted to project'
        }
    
    # Initialize project data
    if not project_data:
        project_data = {}
    
    # Fill in defaults from bid
    project_data.setdefault('name', bid['name'])
    project_data.setdefault('client_id', bid['client_id'])
    project_data.setdefault('budget', bid['total_amount'])
    project_data.setdefault('status', 'Planning')
    project_data.setdefault('description', bid['description'])
    
    # Create project
    from app.services.projects import create_project
    project_id = create_project(project_data)
    
    if project_id:
        # Link bid to project
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE bids SET project_id = ?, updated_at = ? WHERE id = ?",
            (project_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), bid_id)
        )
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'project_id': project_id,
            'message': 'Bid successfully converted to project'
        }
    
    return {
        'success': False,
        'message': 'Failed to create project'
    } 