"""
Unit tests for documents service
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.services.documents import (
    get_all_documents,
    get_document,
    get_entity_documents,
    save_uploaded_file,
    create_document,
    update_document,
    delete_document,
    get_file_type_icon,
    count_documents_by_entity,
    search_documents_by_content,
    get_document_categories,
    get_latest_documents,
    check_file_exists,
    is_allowed_file
)

@pytest.fixture
def mock_document():
    return {
        'id': 'doc_001',
        'title': 'Test Document',
        'description': 'Test Description',
        'file_path': '/test/path/document.pdf',
        'file_type': 'pdf',
        'file_size': 1024,
        'entity_type': 'project',
        'entity_id': 'proj_001',
        'category': 'Estimates',
        'created_by': 'user_001',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

@pytest.fixture
def mock_file():
    file = MagicMock()
    file.filename = 'test.pdf'
    file.content_type = 'application/pdf'
    return file

def test_get_all_documents():
    with patch('app.services.documents.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.execute.return_value.data = [{'id': 'doc_001'}]
        
        documents = get_all_documents()
        assert len(documents) == 1
        assert documents[0]['id'] == 'doc_001'
        mock_supabase.from_.assert_called_once()

def test_get_document():
    with patch('app.services.documents.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'doc_001'}]
        
        document = get_document('doc_001')
        assert document is not None
        assert document['id'] == 'doc_001'
        mock_supabase.from_.assert_called_once()

def test_get_entity_documents():
    with patch('app.services.documents.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{'id': 'doc_001'}]
        
        documents = get_entity_documents('project', 'proj_001')
        assert len(documents) == 1
        assert documents[0]['id'] == 'doc_001'
        mock_supabase.from_.assert_called_once()

def test_save_uploaded_file(mock_file):
    with patch('app.services.documents.secure_filename') as mock_secure:
        mock_secure.return_value = 'test.pdf'
        
        with patch('app.services.documents.os.path.join') as mock_join:
            mock_join.return_value = '/test/path/test.pdf'
            
            with patch('app.services.documents.os.makedirs') as mock_makedirs:
                with patch('app.services.documents.os.path.exists') as mock_exists:
                    mock_exists.return_value = False
                    
                    file_path = save_uploaded_file(mock_file, '/test/path')
                    assert file_path == '/test/path/test.pdf'
                    mock_secure.assert_called_once()
                    mock_join.assert_called_once()
                    mock_makedirs.assert_called_once()

def test_create_document(mock_document):
    with patch('app.services.documents.supabase') as mock_supabase:
        mock_supabase.from_.return_value.insert.return_value.execute.return_value.data = [mock_document]
        
        document = create_document(mock_document)
        assert document is not None
        assert document['id'] == mock_document['id']
        mock_supabase.from_.assert_called_once()

def test_update_document(mock_document):
    with patch('app.services.documents.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_document]
        
        document = update_document('doc_001', mock_document)
        assert document is not None
        assert document['id'] == mock_document['id']
        mock_supabase.from_.assert_called_once()

def test_delete_document():
    with patch('app.services.documents.supabase') as mock_supabase:
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = True
        
        result = delete_document('doc_001')
        assert result is True
        mock_supabase.from_.assert_called_once()

def test_get_file_type_icon():
    icon = get_file_type_icon('pdf')
    assert icon == 'fa-file-pdf'

def test_count_documents_by_entity():
    with patch('app.services.documents.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.count = 5
        
        count = count_documents_by_entity('project', 'proj_001')
        assert count == 5
        mock_supabase.from_.assert_called_once()

def test_search_documents_by_content():
    with patch('app.services.documents.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.ilike.return_value.execute.return_value.data = [{'id': 'doc_001'}]
        
        documents = search_documents_by_content('test')
        assert len(documents) == 1
        assert documents[0]['id'] == 'doc_001'
        mock_supabase.from_.assert_called_once()

def test_get_document_categories():
    categories = get_document_categories()
    assert len(categories) > 0
    assert 'Estimates' in categories

def test_get_latest_documents():
    with patch('app.services.documents.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [{'id': 'doc_001'}]
        
        documents = get_latest_documents(5)
        assert len(documents) == 1
        assert documents[0]['id'] == 'doc_001'
        mock_supabase.from_.assert_called_once()

def test_check_file_exists():
    with patch('app.services.documents.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{'id': 'doc_001'}]
        
        exists = check_file_exists('project', 'proj_001', 'test.pdf')
        assert exists is True
        mock_supabase.from_.assert_called_once()

def test_is_allowed_file():
    assert is_allowed_file('test.pdf') is True
    assert is_allowed_file('test.exe') is False 