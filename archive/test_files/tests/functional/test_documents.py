import pytest
import os
import io
from app.db import get_db
from werkzeug.datastructures import FileStorage

@pytest.mark.functional
class TestDocuments:
    
    def test_document_list(self, with_admin_user):
        """Test listing documents."""
        response = with_admin_user.get('/documents/')
        assert response.status_code == 200
        assert b'Contract.pdf' in response.data
        assert b'Blueprint.jpg' in response.data
    
    def test_document_detail(self, with_admin_user):
        """Test viewing document details."""
        response = with_admin_user.get('/documents/1')
        assert response.status_code == 200
        assert b'Contract.pdf' in response.data
        assert b'Project contract' in response.data
    
    def test_upload_document(self, with_admin_user, app, tmpdir):
        """Test uploading a document."""
        # Create a temporary file for testing
        test_file = os.path.join(tmpdir, 'test_upload.pdf')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        # Create file storage object
        with open(test_file, 'rb') as f:
            file = FileStorage(
                stream=io.BytesIO(f.read()),
                filename='test_upload.pdf',
                content_type='application/pdf'
            )
        
        # Upload the file
        data = {
            'file': file,
            'description': 'Test upload document',
            'client_id': '1',
            'project_id': '1'
        }
        
        response = with_admin_user.post(
            '/documents/upload',
            data=data,
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'Document uploaded successfully' in response.data or b'test_upload.pdf' in response.data
        
        # Verify document was added to the database
        with app.app_context():
            db = get_db()
            document = db.execute(
                "SELECT * FROM documents WHERE name = 'test_upload.pdf'"
            ).fetchone()
            assert document is not None
            assert document['description'] == 'Test upload document'
            assert document['type'] == 'PDF'
    
    def test_document_share(self, with_admin_user):
        """Test document sharing form."""
        response = with_admin_user.get('/documents/share/1')
        assert response.status_code == 200
        assert b'Share Document' in response.data
        assert b'Contract.pdf' in response.data
    
    def test_share_document(self, with_admin_user, app):
        """Test sharing a document via email."""
        data = {
            'recipient_email': 'test@example.com',
            'message': 'Here is the document you requested.'
        }
        
        # Mock the email sending functionality
        with app.test_request_context():
            # Set up session data
            with with_admin_user.session_transaction() as sess:
                sess['user_name'] = 'Admin User'
        
        response = with_admin_user.post(
            '/documents/share/1',
            data=data,
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'Document shared successfully' in response.data or b'shared with test@example.com' in response.data
    
    def test_document_download(self, with_admin_user, app, monkeypatch):
        """Test downloading a document."""
        # Mock the file existence check
        monkeypatch.setattr('os.path.exists', lambda path: True)
        
        # Mock the send_from_directory function
        def mock_send_from_directory(directory, filename, as_attachment=False):
            return f"Sent {filename} from {directory}"
        
        monkeypatch.setattr('app.routes.documents.send_from_directory', mock_send_from_directory)
        
        response = with_admin_user.get('/documents/download/1')
        assert response.status_code == 200
    
    def test_document_delete(self, with_admin_user, app):
        """Test deleting a document."""
        # Create a test document to delete
        with app.app_context():
            db = get_db()
            db.execute(
                """INSERT INTO documents
                   (name, description, type, size, path, uploaded_by, client_id, project_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                ('test_delete.pdf', 'Test delete document', 'PDF', 1024, 'path/to/test_delete.pdf', 1, 1, 1)
            )
            db.commit()
            document_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        response = with_admin_user.post(
            f'/documents/{document_id}/delete',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'Document deleted successfully' in response.data or b'deleted' in response.data
        
        # Verify document was deleted from the database
        with app.app_context():
            db = get_db()
            document = db.execute(
                f"SELECT * FROM documents WHERE id = {document_id}"
            ).fetchone()
            assert document is None
    
    def test_client_documents(self, with_admin_user, test_client_id):
        """Test viewing documents for a specific client."""
        response = with_admin_user.get(f'/documents/client/{test_client_id}')
        assert response.status_code == 200
        assert b'Contract.pdf' in response.data
        assert b'Test Client 1' in response.data
    
    def test_project_documents(self, with_admin_user, test_project_id):
        """Test viewing documents for a specific project."""
        response = with_admin_user.get(f'/documents/project/{test_project_id}')
        assert response.status_code == 200
        assert b'Contract.pdf' in response.data
        assert b'Test Project 1' in response.data
    
    def test_unauthorized_document_access(self, client):
        """Test unauthorized access to document pages."""
        # Try accessing documents without login
        response = client.get('/documents/', follow_redirects=True)
        assert response.status_code == 200
        assert b'Log In' in response.data 