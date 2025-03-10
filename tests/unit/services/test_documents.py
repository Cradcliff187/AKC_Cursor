"""
Unit tests for documents service
"""
import pytest
import os
from io import BytesIO
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage
from app.services.documents import (
    get_all_documents, get_document, get_entity_documents,
    save_uploaded_file, create_document, update_document,
    delete_document, get_file_type_icon
)

class TestDocumentsService:
    """Test suite for documents service"""

    def test_get_all_documents(self, app, monkeypatch):
        """Test retrieving all documents"""
        # Mock database query result
        mock_result = [
            {'id': 1, 'name': 'Document 1', 'file_path': 'path/to/doc1.pdf'},
            {'id': 2, 'name': 'Document 2', 'file_path': 'path/to/doc2.jpg'},
        ]
        
        # Mock execute method
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = mock_result
        
        # Mock db connection and execute
        mock_db = MagicMock()
        mock_db.execute.return_value = mock_execute
        
        # Patch get_db to return our mock
        monkeypatch.setattr('app.services.documents.get_db', lambda: mock_db)
        
        with app.app_context():
            # Test default parameters
            documents = get_all_documents()
            assert documents == mock_result
            mock_db.execute.assert_called_once()
            
            # Reset mocks for next test
            mock_db.reset_mock()
            
            # Test with filters
            documents = get_all_documents(
                limit=10, 
                offset=5, 
                search='test'
            )
            assert documents == mock_result
            mock_db.execute.assert_called_once()
            
            # Check that params were passed
            call_args = mock_db.execute.call_args[0]
            assert 'LIMIT ? OFFSET ?' in call_args[0]
            assert 10 in call_args[1]  # limit param
            assert 5 in call_args[1]   # offset param
            assert '%test%' in call_args[1]  # search param

    def test_get_document(self, app, monkeypatch):
        """Test retrieving a single document"""
        # Mock database query result
        mock_document = {
            'id': 1, 
            'name': 'Test Document',
            'file_path': 'path/to/document.pdf',
            'created_by_id': 1,
            'created_by_name': 'Test User'
        }
        
        # Mock execute method
        mock_execute = MagicMock()
        mock_execute.fetchone.return_value = mock_document
        
        # Mock db connection and execute
        mock_db = MagicMock()
        mock_db.execute.return_value = mock_execute
        
        # Patch get_db to return our mock
        monkeypatch.setattr('app.services.documents.get_db', lambda: mock_db)
        
        with app.app_context():
            document = get_document(1)
            assert document == mock_document
            mock_db.execute.assert_called_once()
            
            # Check that the document_id parameter is correctly passed
            # The parameter is passed as a tuple (document_id,)
            args, kwargs = mock_db.execute.call_args
            query, params = args
            assert params[0] == 1  # document_id param

    def test_get_entity_documents(self, app, monkeypatch):
        """Test retrieving documents for an entity"""
        # Mock database query result
        mock_documents = [
            {'id': 1, 'name': 'Document 1', 'file_path': 'path/to/doc1.pdf'},
            {'id': 2, 'name': 'Document 2', 'file_path': 'path/to/doc2.jpg'},
        ]
        
        # Mock execute method
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = mock_documents
        
        # Mock db connection and execute
        mock_db = MagicMock()
        mock_db.execute.return_value = mock_execute
        
        # Patch get_db to return our mock
        monkeypatch.setattr('app.services.documents.get_db', lambda: mock_db)
        
        with app.app_context():
            # Test for project entity
            documents = get_entity_documents('project', 1)
            assert documents == mock_documents
            mock_db.execute.assert_called_once()
            assert 'project_id = ?' in mock_db.execute.call_args[0][0]
            assert 1 in mock_db.execute.call_args[0][1]  # entity_id param
            
            # Reset mock for next test
            mock_db.reset_mock()
            
            # Test for client entity
            documents = get_entity_documents('client', 2)
            assert documents == mock_documents
            mock_db.execute.assert_called_once()
            assert 'client_id = ?' in mock_db.execute.call_args[0][0]
            assert 2 in mock_db.execute.call_args[0][1]  # entity_id param

    def test_save_uploaded_file(self, app, tmp_path):
        """Test saving an uploaded file"""
        # Create a test file
        file_content = b'Test file content'
        test_file = FileStorage(
            stream=BytesIO(file_content),
            filename='test.pdf',
            content_type='application/pdf'
        )
        
        # Create directory for test
        upload_dir = tmp_path
        
        with app.app_context():
            # Save the file
            result = save_uploaded_file(test_file, upload_dir)
            
            # Check the result
            assert result['original_name'] == 'test.pdf'
            assert 'saved_name' in result
            assert result['saved_name'].endswith('test.pdf')
            assert result['type'] == 'application/pdf'
            assert result['size'] == len(file_content)
            
            # Check that the file actually exists
            assert os.path.exists(result['path'])
            assert os.path.getsize(result['path']) == len(file_content)
            
            # Check file content
            with open(result['path'], 'rb') as f:
                saved_content = f.read()
            assert saved_content == file_content

    def test_create_document(self, app, monkeypatch):
        """Test creating a document record"""
        # Mock cursor with lastrowid
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        
        # Mock database connection
        mock_db = MagicMock()
        mock_db.execute.return_value = mock_cursor
        
        # Patch get_db to return our mock
        monkeypatch.setattr('app.services.documents.get_db', lambda: mock_db)
        
        document_data = {
            'name': 'Test Document',
            'file_path': 'path/to/document.pdf',
            'file_type': 'application/pdf',
            'file_size': 1024,
            'project_id': 1,
            'description': 'Test document description',
            'created_by_id': 1
        }
        
        with app.app_context():
            doc_id = create_document(document_data)
            
            # Check the return value
            assert doc_id == 1
            
            # Check that execute was called with the right params
            mock_db.execute.assert_called_once()
            mock_db.commit.assert_called_once()
            
            # Check first param (the SQL query)
            sql = mock_db.execute.call_args[0][0]
            assert 'INSERT INTO documents' in sql
            assert 'name' in sql
            assert 'file_path' in sql
            
            # Check that all fields were included in the params
            params = mock_db.execute.call_args[0][1]
            assert document_data['name'] in params
            assert document_data['file_path'] in params
            assert document_data['file_type'] in params
            assert document_data['file_size'] in params
            assert document_data['project_id'] in params
            assert document_data['description'] in params
            assert document_data['created_by_id'] in params

    def test_update_document(self, app, monkeypatch):
        """Test updating a document record"""
        # Mock database connection
        mock_db = MagicMock()
        
        # Patch get_db to return our mock
        monkeypatch.setattr('app.services.documents.get_db', lambda: mock_db)
        
        update_data = {
            'name': 'Updated Document',
            'description': 'Updated description',
            'project_id': 2
        }
        
        with app.app_context():
            result = update_document(1, update_data)
            
            # Check the return value
            assert result is True
            
            # Check that execute was called with the right params
            mock_db.execute.assert_called_once()
            mock_db.commit.assert_called_once()
            
            # Check first param (the SQL query)
            sql = mock_db.execute.call_args[0][0]
            assert 'UPDATE documents SET' in sql
            assert 'name = ?' in sql
            assert 'description = ?' in sql
            assert 'project_id = ?' in sql
            assert 'WHERE id = ?' in sql
            
            # Check that all fields were included in the params
            params = mock_db.execute.call_args[0][1]
            assert update_data['name'] in params
            assert update_data['description'] in params
            assert update_data['project_id'] in params
            assert 1 in params  # document_id
            
        # Test with no fields to update
        mock_db.reset_mock()
        with app.app_context():
            result = update_document(1, {})
            
            # Should return False if no fields to update
            assert result is False
            
            # Execute should not be called
            mock_db.execute.assert_not_called()
            mock_db.commit.assert_not_called()

    def test_delete_document(self, app, monkeypatch):
        """Test deleting a document record"""
        # Mock get_document result
        mock_document = {
            'id': 1,
            'name': 'Test Document',
            'file_path': '/fake/path/doc.pdf'
        }
        
        # Mock functions
        mock_get_document = MagicMock(return_value=mock_document)
        monkeypatch.setattr('app.services.documents.get_document', mock_get_document)
        
        # Mock database connection
        mock_db = MagicMock()
        monkeypatch.setattr('app.services.documents.get_db', lambda: mock_db)
        
        # Mock os.path.exists and os.remove
        monkeypatch.setattr('os.path.exists', lambda path: True)
        mock_remove = MagicMock()
        monkeypatch.setattr('os.remove', mock_remove)
        
        with app.app_context():
            result = delete_document(1)
            
            # Check the return value
            assert result is True
            
            # Check that the document was queried
            mock_get_document.assert_called_once_with(1)
            
            # Check that execute was called with the right params
            mock_db.execute.assert_called_once()
            assert 'DELETE FROM documents WHERE id = ?' in mock_db.execute.call_args[0][0]
            assert 1 in mock_db.execute.call_args[0][1]  # document_id
            
            # Check that commit was called
            mock_db.commit.assert_called_once()
            
            # Check that the file was deleted
            mock_remove.assert_called_once_with('/fake/path/doc.pdf')
            
        # Test with document not found
        mock_get_document.return_value = None
        mock_db.reset_mock()
        mock_remove.reset_mock()
        
        with app.app_context():
            result = delete_document(2)
            
            # Should return False if document not found
            assert result is False
            
            # Execute and remove should not be called
            mock_db.execute.assert_not_called()
            mock_db.commit.assert_not_called()
            mock_remove.assert_not_called()

    def test_get_file_type_icon(self):
        """Test getting file type icon class based on MIME type"""
        # Test image types
        assert 'fa-file-image' in get_file_type_icon('image/jpeg')
        assert 'fa-file-image' in get_file_type_icon('image/png')
        assert 'fa-file-image' in get_file_type_icon('image/gif')
        
        # Test PDF
        assert 'fa-file-pdf' in get_file_type_icon('application/pdf')
        
        # Test Office documents
        assert 'fa-file-word' in get_file_type_icon('application/msword')
        assert 'fa-file-word' in get_file_type_icon('application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        assert 'fa-file-excel' in get_file_type_icon('application/vnd.ms-excel')
        assert 'fa-file-excel' in get_file_type_icon('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        assert 'fa-file-powerpoint' in get_file_type_icon('application/vnd.ms-powerpoint')
        
        # Test text files
        assert 'fa-file-alt' in get_file_type_icon('text/plain')
        assert 'fa-file-alt' in get_file_type_icon('text/csv')
        
        # Test compressed files
        assert 'fa-file-archive' in get_file_type_icon('application/zip')
        assert 'fa-file-archive' in get_file_type_icon('application/x-rar-compressed')
        
        # Test audio files
        assert 'fa-file-audio' in get_file_type_icon('audio/mpeg')
        
        # Test video files
        assert 'fa-file-video' in get_file_type_icon('video/mp4')
        
        # Test CAD files
        assert 'fa-drafting-compass' in get_file_type_icon('application/dxf')
        
        # Test default icon for unknown types
        assert 'fa-file' in get_file_type_icon('application/unknown')
        assert 'fa-file' in get_file_type_icon(None)
        assert 'fa-file' in get_file_type_icon('') 