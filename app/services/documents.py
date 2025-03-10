from app.services.supabase import supabase
import uuid
import os
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import werkzeug
from app.services.utils import generate_document_id, generate_folder_name
from app.db import get_db

# File Storage Structure as defined in the JSON guide
FOLDER_STRUCTURE = {
    'projectFolder': '{CustomerID}-{ProjectID}-{ProjectName}',
    'subfolders': [
        'Estimates',
        'Materials',
        'SubInvoices'
    ]
}

# Define allowed file types
ALLOWED_FILE_TYPES = {
    'images': ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'],
    'documents': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'],
    'spreadsheets': ['xls', 'xlsx', 'csv', 'ods'],
    'plans': ['dwg', 'dxf', 'pdf'],
    'presentations': ['ppt', 'pptx', 'odp']
}

# Maps file extensions to icon classes
FILE_TYPE_ICONS = {
    # Images
    'jpg': 'fa-file-image',
    'jpeg': 'fa-file-image',
    'png': 'fa-file-image',
    'gif': 'fa-file-image',
    'svg': 'fa-file-image',
    'webp': 'fa-file-image',
    
    # Documents
    'pdf': 'fa-file-pdf',
    'doc': 'fa-file-word',
    'docx': 'fa-file-word',
    'txt': 'fa-file-alt',
    'rtf': 'fa-file-alt',
    'odt': 'fa-file-alt',
    
    # Spreadsheets
    'xls': 'fa-file-excel',
    'xlsx': 'fa-file-excel',
    'csv': 'fa-file-csv',
    'ods': 'fa-file-excel',
    
    # Presentations
    'ppt': 'fa-file-powerpoint',
    'pptx': 'fa-file-powerpoint',
    'odp': 'fa-file-powerpoint',
    
    # Plans
    'dwg': 'fa-drafting-compass',
    'dxf': 'fa-drafting-compass',
    
    # Default
    'default': 'fa-file'
}

# Mock data for documents
MOCK_DOCUMENTS = [
    {
        'id': '1',
        'name': 'Blueprint-v1.pdf',
        'description': 'Initial blueprint design',
        'file_path': 'uploads/projects/CUST001-PRJ001-MainOfficeRenovation/blueprint-v1.pdf',
        'file_type': 'application/pdf',
        'file_size': 2458920,
        'entity_type': 'project',
        'entity_id': '1',
        'uploaded_by': 'admin',
        'uploaded_at': (datetime.now()).isoformat(),
        'updated_at': (datetime.now()).isoformat()
    },
    {
        'id': '2',
        'name': 'Client Contract.docx',
        'description': 'Signed contract',
        'entity_type': 'client',
        'entity_id': '1',
        'file_path': 'uploads/clients/1/contract.docx',
        'file_type': 'docx',
        'file_size': 1536,
        'uploaded_by': 'admin',
        'created_at': '2023-01-20T14:15:00',
        'updated_at': None
    },
    {
        'id': '3',
        'name': 'Material Invoice.pdf',
        'description': 'Invoice for materials',
        'entity_type': 'vendor',
        'entity_id': '1',
        'file_path': 'uploads/vendors/1/invoice.pdf',
        'file_type': 'pdf',
        'file_size': 1024,
        'uploaded_by': 'admin',
        'created_at': '2023-02-05T10:45:00',
        'updated_at': None
    },
    {
        'id': '4',
        'name': 'Subcontractor Agreement.pdf',
        'description': 'Signed agreement',
        'entity_type': 'subcontractor',
        'entity_id': '1',
        'file_path': 'uploads/subcontractors/1/agreement.pdf',
        'file_type': 'pdf',
        'file_size': 3072,
        'uploaded_by': 'admin',
        'created_at': '2023-02-10T11:20:00',
        'updated_at': None
    },
    {
        'id': '5',
        'name': 'Project Timeline.xlsx',
        'description': 'Detailed project timeline',
        'entity_type': 'project',
        'entity_id': '2',
        'file_path': 'uploads/projects/2/timeline.xlsx',
        'file_type': 'xlsx',
        'file_size': 768,
        'uploaded_by': 'admin',
        'created_at': '2023-03-01T08:15:00',
        'updated_at': None
    }
]

def get_all_documents(limit=50, offset=0, search=None):
    """Get all documents with optional filtering"""
    db = get_db()
    query = """
        SELECT d.*, c.name as client_name, p.name as project_name
        FROM documents d
        LEFT JOIN clients c ON d.client_id = c.id
        LEFT JOIN projects p ON d.project_id = p.id
    """
    params = []
    
    if search:
        query += " WHERE d.name LIKE ? OR d.description LIKE ?"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])
    
    query += " ORDER BY d.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    return db.execute(query, params).fetchall()

def get_document(document_id):
    """Get a document by ID"""
    db = get_db()
    return db.execute(
        """SELECT d.*, u.username as created_by_name 
           FROM documents d
           LEFT JOIN users u ON d.created_by_id = u.id
           WHERE d.id = ?""", 
        (document_id,)
    ).fetchone()

def get_entity_documents(entity_type, entity_id):
    """Get documents for a specific entity (client or project)"""
    db = get_db()
    query = f"SELECT * FROM documents WHERE {entity_type}_id = ? ORDER BY created_at DESC"
    return db.execute(query, (entity_id,)).fetchall()

def save_uploaded_file(file, directory):
    """Save an uploaded file to disk"""
    # Create a unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    # Save the file
    file_path = os.path.join(directory, unique_filename)
    file.save(file_path)
    
    return {
        'original_name': filename,
        'saved_name': unique_filename,
        'path': file_path,
        'size': os.path.getsize(file_path),
        'type': file.content_type if hasattr(file, 'content_type') else None
    }
    
def create_document(document_data):
    """Create a new document record"""
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO documents 
        (name, file_path, file_type, file_size, project_id, client_id, 
         description, version, created_by_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            document_data['name'],
            document_data['file_path'],
            document_data['file_type'],
            document_data['file_size'],
            document_data.get('project_id'),
            document_data.get('client_id'),
            document_data.get('description'),
            document_data.get('version', '1.0'),
            document_data.get('created_by_id')
        )
    )
    db.commit()
    return cursor.lastrowid

def update_document(document_id, update_data):
    """Update document information"""
    db = get_db()
    
    # Build the update query dynamically
    fields = []
    params = []
    
    for key, value in update_data.items():
        if key not in ('id', 'created_at', 'file_path'):  # Don't allow updating these fields
            fields.append(f"{key} = ?")
            params.append(value)
    
    if not fields:
        return False
    
    params.append(document_id)
    
    db.execute(
        f"UPDATE documents SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        params
    )
    db.commit()
    return True

def delete_document(document_id):
    """Delete a document record (and optionally file)"""
    # Get the document to find the file path
    document = get_document(document_id)
    if not document:
        return False
    
    # Delete from database
    db = get_db()
    db.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    db.commit()
    
    # Delete the file if it exists
    file_path = document['file_path']
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    return True

def get_file_type_icon(file_type):
    """Returns an icon class based on file type"""
    if not file_type:
        return "fas fa-file"
        
    file_type = file_type.lower()
    
    # Images
    if file_type.startswith('image/'):
        return "fas fa-file-image"
    
    # PDFs
    if file_type == 'application/pdf':
        return "fas fa-file-pdf"
    
    # Word documents
    if file_type in ('application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'):
        return "fas fa-file-word"
    
    # Excel documents
    if file_type in ('application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
        return "fas fa-file-excel"
    
    # PowerPoint
    if file_type in ('application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'):
        return "fas fa-file-powerpoint"
    
    # Text files
    if file_type in ('text/plain', 'text/csv', 'text/html'):
        return "fas fa-file-alt"
    
    # Compressed files
    if file_type in ('application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed'):
        return "fas fa-file-archive"
    
    # Audio files
    if file_type.startswith('audio/'):
        return "fas fa-file-audio"
    
    # Video files
    if file_type.startswith('video/'):
        return "fas fa-file-video"
    
    # CAD/construction files
    if file_type in ('application/dxf', 'application/dwg', 'application/acad', 'application/step'):
        return "fas fa-drafting-compass"
    
    # Default
    return "fas fa-file"

def count_documents_by_entity(entity_type, entity_id=None):
    """Count documents for a specific entity type or entity"""
    try:
        if entity_id:
            documents = get_entity_documents(entity_type, entity_id)
            return len(documents)
        else:
            all_docs = get_all_documents()
            return len([doc for doc in all_docs if doc['entity_type'] == entity_type])
    except Exception as e:
        print(f"Error counting documents: {str(e)}")
        return 0

def search_documents_by_content(query):
    """Search documents by content (mock implementation)"""
    # Note: In a real implementation, this would use a full-text search engine
    # or a database with text search capabilities.
    # For now, we'll just search in the name and description.
    if not query:
        return []
        
    query = query.lower()
    all_docs = get_all_documents()
    
    return [
        doc for doc in all_docs 
        if query in doc.get('name', '').lower() or 
           query in doc.get('description', '').lower()
    ]

def get_document_categories():
    """Get document category statistics"""
    all_docs = get_all_documents()
    
    # Count documents by entity type
    categories = {}
    for doc in all_docs:
        entity_type = doc.get('entity_type', 'unknown')
        if entity_type in categories:
            categories[entity_type] += 1
        else:
            categories[entity_type] = 1
            
    return categories

def get_latest_documents(limit=5):
    """Get the most recently uploaded documents"""
    all_docs = get_all_documents()
    
    # Sort by uploaded_at in descending order
    sorted_docs = sorted(
        all_docs,
        key=lambda doc: doc.get('uploaded_at', '1970-01-01T00:00:00'),
        reverse=True
    )
    
    return sorted_docs[:limit]

def check_file_exists(entity_type, entity_id, filename):
    """Check if a file already exists in the specified location"""
    # For project documents
    if entity_type == 'project':
        from app.services.projects import get_project_by_id
        from app.services.clients import get_client_by_id
        
        project = get_project_by_id(entity_id)
        if project and project.get('client_id'):
            client = get_client_by_id(project['client_id'])
            customer_id = client.get('id', 'CUST-UNKNOWN')
            project_id = project.get('id', 'PROJ-UNKNOWN')
            project_name = project.get('name', 'Unnamed Project')
            
            folder_name = generate_folder_name(customer_id, project_id, project_name)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'projects', folder_name, filename)
            
            return os.path.exists(file_path)
    
    # For other entity types
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], entity_type, str(entity_id), filename)
    return os.path.exists(file_path)

def is_allowed_file(filename):
    """Check if the file type is allowed"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    
    # Check against all allowed extensions
    for category in ALLOWED_FILE_TYPES.values():
        if extension in category:
            return True
            
    return False 