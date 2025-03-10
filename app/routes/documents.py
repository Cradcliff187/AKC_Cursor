from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, jsonify, send_from_directory,
    current_app, abort
)
from app.routes.auth import login_required
from app.services.documents import (
    get_all_documents, get_document, get_entity_documents,
    save_uploaded_file, delete_document, update_document,
    get_file_type_icon
)
from app.services.projects import get_all_projects, get_project_by_id
from app.services.clients import get_all_clients, get_client_by_id
import os
from werkzeug.utils import secure_filename

bp = Blueprint('documents', __name__, url_prefix='/documents')

@bp.route('/')
@login_required
def list_documents():
    """List all documents"""
    documents = get_all_documents()
    
    # Get filter params if any
    entity_type = request.args.get('type')
    entity_id = request.args.get('id')
    query = request.args.get('query')
    
    # Apply filters if provided
    if entity_type and entity_id:
        documents = get_entity_documents(entity_type, entity_id)
    
    # Apply search query if provided
    if query:
        query = query.lower()
        documents = [
            doc for doc in documents 
            if query in doc.get('name', '').lower() or 
               query in doc.get('description', '').lower()
        ]
    
    # Get projects and clients for filter dropdowns
    projects = get_all_projects()
    clients = get_all_clients()
    
    return render_template(
        'documents/list.html', 
        documents=documents,
        projects=projects,
        clients=clients,
        current_filter={
            'type': entity_type,
            'id': entity_id,
            'query': query
        }
    )

@bp.route('/project/<project_id>')
@login_required
def project_documents(project_id):
    """List documents for a specific project"""
    documents = get_entity_documents('project', project_id)
    project = get_project_by_id(project_id)
    
    return render_template(
        'documents/project_documents.html', 
        documents=documents,
        project=project
    )

@bp.route('/client/<client_id>')
@login_required
def client_documents(client_id):
    """List documents for a specific client"""
    documents = get_entity_documents('client', client_id)
    client = get_client_by_id(client_id)
    
    return render_template(
        'documents/client_documents.html', 
        documents=documents,
        client=client
    )

@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload_document():
    """Upload a new document"""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        entity_type = request.form['entity_type']
        entity_id = request.form['entity_id']
        description = request.form.get('description', '')
        
        # Save the uploaded file
        document = save_uploaded_file(file, entity_type, entity_id, description)
        
        if document:
            flash('Document uploaded successfully!')
            
            # Redirect based on entity type
            if entity_type == 'project':
                return redirect(url_for('documents.project_documents', project_id=entity_id))
            elif entity_type == 'client':
                return redirect(url_for('documents.client_documents', client_id=entity_id))
            else:
                return redirect(url_for('documents.list_documents'))
        else:
            flash('Error uploading document')
    
    # Get entity information for the form
    projects = get_all_projects()
    clients = get_all_clients()
    
    # Check if we're uploading for a specific entity
    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id')
    
    entity = None
    if entity_type == 'project' and entity_id:
        entity = get_project_by_id(entity_id)
    elif entity_type == 'client' and entity_id:
        entity = get_client_by_id(entity_id)
    
    return render_template(
        'documents/upload.html',
        projects=projects,
        clients=clients,
        entity_type=entity_type,
        entity_id=entity_id,
        entity=entity
    )

@bp.route('/<document_id>')
@login_required
def document_detail(document_id):
    """View document details"""
    document = get_document(document_id)
    
    if not document:
        flash('Document not found')
        return redirect(url_for('documents.list_documents'))
    
    # Get related entity
    entity = None
    if document['entity_type'] == 'project':
        entity = get_project_by_id(document['entity_id'])
    elif document['entity_type'] == 'client':
        entity = get_client_by_id(document['entity_id'])
    
    return render_template(
        'documents/detail.html',
        document=document,
        entity=entity,
        file_icon=get_file_type_icon(document.get('file_type'))
    )

@bp.route('/download/<document_id>')
@login_required
def download_document(document_id):
    """Download a document"""
    document = get_document(document_id)
    
    if not document or not document.get('file_path'):
        flash('Document not found or no file available')
        return redirect(url_for('documents.list_documents'))
    
    # Extract directory and filename
    file_path = document['file_path']
    if file_path.startswith('uploads/'):
        file_path = file_path[8:]  # Remove 'uploads/' prefix
    
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    # Construct full path to ensure it exists
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path)
    if not os.path.exists(full_path):
        flash('File not found on server')
        return redirect(url_for('documents.document_detail', document_id=document_id))
    
    # Serve the file
    return send_from_directory(
        os.path.join(current_app.config['UPLOAD_FOLDER'], directory),
        filename,
        as_attachment=True
    )

@bp.route('/delete/<document_id>', methods=['POST'])
@login_required
def delete_document_route(document_id):
    """Delete a document"""
    document = get_document(document_id)
    
    if not document:
        flash('Document not found')
        return redirect(url_for('documents.list_documents'))
    
    # Remember entity info for redirection
    entity_type = document.get('entity_type')
    entity_id = document.get('entity_id')
    
    # Attempt to delete
    if delete_document(document_id):
        flash('Document deleted successfully')
    else:
        flash('Error deleting document')
    
    # Redirect based on entity type
    if entity_type == 'project':
        return redirect(url_for('documents.project_documents', project_id=entity_id))
    elif entity_type == 'client':
        return redirect(url_for('documents.client_documents', client_id=entity_id))
    else:
        return redirect(url_for('documents.list_documents'))

@bp.route('/edit/<document_id>', methods=('GET', 'POST'))
@login_required
def edit_document(document_id):
    """Edit document metadata"""
    document = get_document(document_id)
    
    if not document:
        flash('Document not found')
        return redirect(url_for('documents.list_documents'))
    
    if request.method == 'POST':
        # Update document metadata
        data = {
            'name': request.form.get('name', document['name']),
            'description': request.form.get('description', document.get('description', '')),
        }
        
        if update_document(document_id, data):
            flash('Document updated successfully')
            return redirect(url_for('documents.document_detail', document_id=document_id))
        else:
            flash('Error updating document')
    
    return render_template(
        'documents/edit.html',
        document=document
    )

@bp.route('/search')
@login_required
def search_documents():
    """Search for documents"""
    query = request.args.get('query', '')
    
    if not query:
        return redirect(url_for('documents.list_documents'))
    
    # Search documents
    all_documents = get_all_documents()
    
    # Simple search by name and description
    documents = [
        doc for doc in all_documents 
        if query.lower() in doc.get('name', '').lower() or 
           query.lower() in doc.get('description', '').lower()
    ]
    
    return render_template(
        'documents/list.html',
        documents=documents,
        query=query,
        search_results=True,
        projects=[],
        clients=[],
        current_filter={'query': query}
    )

@bp.route('/api/documents')
@login_required
def api_documents():
    """API endpoint to get documents"""
    entity_type = request.args.get('type')
    entity_id = request.args.get('id')
    
    if entity_type and entity_id:
        documents = get_entity_documents(entity_type, entity_id)
    else:
        documents = get_all_documents()
    
    return jsonify(documents) 