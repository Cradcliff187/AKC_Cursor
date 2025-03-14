"""
Mock clients service for testing.
In a real application, this would handle client data operations.
"""
from app.db import get_db

def get_all_clients(limit=50, offset=0, search=None):
    """Get all clients with optional filtering"""
    db = get_db()
    query = "SELECT * FROM clients"
    params = []
    
    if search:
        query += " WHERE name LIKE ? OR contact_name LIKE ? OR email LIKE ?"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
    
    query += " ORDER BY name LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    return db.execute(query, params).fetchall()

def get_client_by_id(client_id):
    """Get a client by ID"""
    db = get_db()
    return db.execute(
        "SELECT * FROM clients WHERE id = ?", 
        (client_id,)
    ).fetchone()

def create_client(client_data):
    """Create a new client"""
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO clients 
        (name, contact_name, email, phone, address, city, state, zip_code, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            client_data['name'],
            client_data.get('contact_name'),
            client_data.get('email'),
            client_data.get('phone'),
            client_data.get('address'),
            client_data.get('city'),
            client_data.get('state'),
            client_data.get('zip_code'),
            client_data.get('notes')
        )
    )
    db.commit()
    return cursor.lastrowid

def update_client(client_id, client_data):
    """Update a client"""
    db = get_db()
    db.execute(
        """
        UPDATE clients 
        SET name = ?, contact_name = ?, email = ?, phone = ?, 
            address = ?, city = ?, state = ?, zip_code = ?, notes = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            client_data['name'],
            client_data.get('contact_name'),
            client_data.get('email'),
            client_data.get('phone'),
            client_data.get('address'),
            client_data.get('city'),
            client_data.get('state'),
            client_data.get('zip_code'),
            client_data.get('notes'),
            client_id
        )
    )
    db.commit()
    return True

def delete_client(client_id):
    """Delete a client"""
    db = get_db()
    db.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    db.commit()
    return True

def get_client_projects(client_id):
    """Get all projects for a client"""
    db = get_db()
    return db.execute(
        "SELECT * FROM projects WHERE client_id = ? ORDER BY name",
        (client_id,)
    ).fetchall()

def get_client_invoices(client_id):
    """Get all invoices for a client"""
    db = get_db()
    return db.execute(
        "SELECT * FROM invoices WHERE client_id = ? ORDER BY issue_date DESC",
        (client_id,)
    ).fetchall() 