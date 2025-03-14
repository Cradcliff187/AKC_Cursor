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
from app.services.supabase import supabase

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

def get_bids():
    try:
        response = supabase.table('bids').select('*').execute()
        return response.data
    except Exception as e:
        current_app.logger.error(f"Error fetching bids: {str(e)}")
        return []

def get_bid(bid_id):
    try:
        response = supabase.table('bids').select('*').eq('id', bid_id).single().execute()
        return response.data
    except Exception as e:
        current_app.logger.error(f"Error fetching bid {bid_id}: {str(e)}")
        return None

def create_bid(data):
    try:
        data['created_at'] = datetime.utcnow().isoformat()
        data['updated_at'] = datetime.utcnow().isoformat()
        response = supabase.table('bids').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        current_app.logger.error(f"Error creating bid: {str(e)}")
        return None

def update_bid(bid_id, data):
    try:
        data['updated_at'] = datetime.utcnow().isoformat()
        response = supabase.table('bids').update(data).eq('id', bid_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        current_app.logger.error(f"Error updating bid {bid_id}: {str(e)}")
        return None

def delete_bid(bid_id):
    try:
        response = supabase.table('bids').delete().eq('id', bid_id).execute()
        return True
    except Exception as e:
        current_app.logger.error(f"Error deleting bid {bid_id}: {str(e)}")
        return False

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