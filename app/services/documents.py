from app.services.supabase import supabase
import uuid
import os
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import werkzeug
from app.services.utils import generate_document_id, generate_folder_name

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

def get_all_documents():
    """Get all documents"""
    try:
        if supabase is not None:
            response = supabase.from_("documents").select("*").execute()
            return response.data
        else:
            return MOCK_DOCUMENTS
    except Exception as e:
        print(f"Error fetching documents: {str(e)}")
        return MOCK_DOCUMENTS

def get_document(document_id):
    """Get a single document by ID"""
    try:
        if supabase is not None:
            response = supabase.from_("documents").select("*").eq("id", document_id).execute()
            if response.data:
                return response.data[0]
        else:
            for doc in MOCK_DOCUMENTS:
                if doc['id'] == document_id:
                    return doc
        return None
    except Exception as e:
        print(f"Error fetching document {document_id}: {str(e)}")
        # Still attempt to return from mock data on error
        for doc in MOCK_DOCUMENTS:
            if doc['id'] == document_id:
                return doc
        return None

def get_entity_documents(entity_type, entity_id):
    """Get all documents for a specific entity (project, client, vendor, etc.)"""
    try:
        if supabase is not None:
            response = supabase.from_("documents").select("*").eq("entity_type", entity_type).eq("entity_id", entity_id).execute()
            return response.data
        else:
            return [doc for doc in MOCK_DOCUMENTS if doc['entity_type'] == entity_type and doc['entity_id'] == str(entity_id)]
    except Exception as e:
        print(f"Error fetching documents for {entity_type} {entity_id}: {str(e)}")
        return [doc for doc in MOCK_DOCUMENTS if doc['entity_type'] == entity_type and doc['entity_id'] == str(entity_id)]

def save_uploaded_file(file, entity_type, entity_id, description=''):
    """Save an uploaded file and return the document record"""
    try:
        if not file:
            return None
            
        # Generate a unique document ID
        doc_id = generate_document_id()
        
        # Get file information
        filename = secure_filename(file.filename)
        file_type = file.content_type
        file_size = 0  # Will be populated after saving the file
        
        # Create documents directory if it doesn't exist
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], entity_type, str(entity_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # If entity_type is 'project', use the folder structure from the guide
        if entity_type == 'project':
            # Get project details to construct folder name
            from app.services.projects import get_project_by_id
            from app.services.clients import get_client_by_id
            
            project = get_project_by_id(entity_id)
            if project and project.get('client_id'):
                client = get_client_by_id(project['client_id'])
                customer_id = client.get('id', 'CUST-UNKNOWN')
                project_id = project.get('id', 'PROJ-UNKNOWN')
                project_name = project.get('name', 'Unnamed Project')
                
                folder_name = generate_folder_name(customer_id, project_id, project_name)
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'projects', folder_name)
                
                # Create appropriate subfolder based on document type
                # This would need to be determined by additional metadata in a real implementation
                if 'invoice' in filename.lower() or 'invoice' in description.lower():
                    upload_dir = os.path.join(upload_dir, 'SubInvoices')
                elif 'estimate' in filename.lower() or 'estimate' in description.lower():
                    upload_dir = os.path.join(upload_dir, 'Estimates')
                elif 'material' in filename.lower() or 'material' in description.lower():
                    upload_dir = os.path.join(upload_dir, 'Materials')
                
                os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Get actual file size
        file_size = os.path.getsize(file_path)
        
        # Determine relative path for storage
        if current_app.config['UPLOAD_FOLDER'] in file_path:
            relative_path = file_path.replace(current_app.config['UPLOAD_FOLDER'], 'uploads')
        else:
            relative_path = os.path.join('uploads', entity_type, str(entity_id), filename)
        
        # Create document record
        document = {
            'id': doc_id,
            'name': filename,
            'description': description,
            'file_path': relative_path,
            'file_type': file_type,
            'file_size': file_size,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'uploaded_by': 'admin',  # In a real app, this would be the current user
            'uploaded_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if supabase is None:
            # Add to mock data
            MOCK_DOCUMENTS.append(document)
        else:
            # Add to database
            response = supabase.from_("documents").insert(document).execute()
            if not response.data:
                return None
            document = response.data[0]
        
        return document
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        # Clean up file if it was created
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        return None

def delete_document(document_id):
    """Delete a document"""
    try:
        # Get the document first to know the file path
        document = get_document(document_id)
        if not document:
            return False
            
        # Delete from database
        if supabase is not None:
            supabase.from_("documents").delete().eq("id", document_id).execute()
        else:
            global MOCK_DOCUMENTS
            MOCK_DOCUMENTS = [doc for doc in MOCK_DOCUMENTS if doc['id'] != document_id]
            
        # Delete file if it exists
        if document.get('file_path'):
            # Convert relative path to full path
            if document['file_path'].startswith('uploads/'):
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document['file_path'][8:])
            else:
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document['file_path'])
                
            if os.path.exists(full_path):
                os.remove(full_path)
                
        return True
    except Exception as e:
        print(f"Error deleting document {document_id}: {str(e)}")
        return False

def update_document(document_id, data):
    """Update document metadata"""
    try:
        # Get existing document
        document = get_document(document_id)
        if not document:
            return False
            
        # Update with new data
        updated_doc = {**document, **data, 'updated_at': datetime.now().isoformat()}
        
        # Save to database
        if supabase is not None:
            response = supabase.from_("documents").update(updated_doc).eq("id", document_id).execute()
            return bool(response.data)
        else:
            # Update in mock data
            global MOCK_DOCUMENTS
            for i, doc in enumerate(MOCK_DOCUMENTS):
                if doc['id'] == document_id:
                    MOCK_DOCUMENTS[i] = updated_doc
                    return True
            return False
    except Exception as e:
        print(f"Error updating document {document_id}: {str(e)}")
        return False

def get_file_type_icon(file_type):
    """Get appropriate icon class for file type"""
    if not file_type:
        return 'fas fa-file'
        
    # Try to determine extension from mime type
    if '/' in file_type:
        extension = mimetypes.guess_extension(file_type)
        if extension and extension.startswith('.'):
            extension = extension[1:]  # Remove the dot
    else:
        # Assume file_type is the extension itself
        extension = file_type.lower()
    
    # Look up icon class
    icon_class = FILE_TYPE_ICONS.get(extension, FILE_TYPE_ICONS['default'])
    return f'fas {icon_class}'

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