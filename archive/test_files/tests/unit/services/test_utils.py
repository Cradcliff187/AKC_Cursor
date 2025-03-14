"""
Unit tests for utilities service
"""
import pytest
import re
from datetime import datetime
from app.services.utils import (
    generate_document_id, generate_folder_name, generate_slug,
    format_currency, format_date, truncate_text
)

def test_generate_document_id():
    """Test generation of document IDs"""
    # Test that IDs are generated with correct format
    doc_id = generate_document_id()
    assert doc_id.startswith('DOC-')
    assert len(doc_id) > 4  # Ensure there's content after the prefix
    
    # Test that IDs are unique
    ids = [generate_document_id() for _ in range(10)]
    assert len(ids) == len(set(ids))  # All IDs should be unique

def test_generate_folder_name():
    """Test generation of folder names"""
    # Test with simple inputs
    folder_name = generate_folder_name('CUST-001', 'PROJ-001', 'Test Project')
    assert 'CUST-001' in folder_name
    assert 'PROJ-001' in folder_name
    assert 'Test_Project' in folder_name
    
    # Test with special characters
    folder_name = generate_folder_name('CUST-001', 'PROJ-001', 'Test & Project #123')
    assert re.search(r'Test_Project_123$', folder_name)
    
    # Test with empty project name
    folder_name = generate_folder_name('CUST-001', 'PROJ-001', '')
    assert folder_name == 'CUST-001_PROJ-001_'
    
    # Test with None project name
    folder_name = generate_folder_name('CUST-001', 'PROJ-001', None)
    assert folder_name == 'CUST-001_PROJ-001_'  # None is converted to empty string

def test_generate_slug():
    """Test slug generation from text"""
    # Test basic slug generation
    assert generate_slug('Hello World') == 'hello-world'
    
    # Test with special characters
    assert generate_slug('Hello & World! #123') == 'hello-world-123'
    
    # Test with multiple spaces and dashes
    assert generate_slug('Hello  -  World') == 'hello-world'
    
    # Test with leading/trailing spaces and dashes
    assert generate_slug(' -Hello World- ') == 'hello-world'
    
    # Test with non-ASCII characters
    assert generate_slug('Café & Résumé') == 'caf-r-sum'
    
    # Test with empty string
    assert generate_slug('') == ''
    
    # Test with None
    assert generate_slug(None) == ''

def test_format_currency():
    """Test currency formatting"""
    # Test basic formatting
    assert format_currency(1000) == '$1,000.00'
    assert format_currency(1000.5) == '$1,000.50'
    
    # Test with different decimal places
    assert format_currency(1000, decimal_places=0) == '$1,000'
    assert format_currency(1000.5, decimal_places=1) == '$1,000.5'
    assert format_currency(1000.567, decimal_places=3) == '$1,000.567'
    
    # Test with different currency symbol
    assert format_currency(1000, symbol='€') == '€1,000.00'
    assert format_currency(1000, symbol='£') == '£1,000.00'
    assert format_currency(1000, symbol='') == '1,000.00'
    
    # Test with negative amount
    assert format_currency(-1000) == '$-1,000.00'
    
    # Test with zero
    assert format_currency(0) == '$0.00'
    
    # Test with None
    assert format_currency(None) == '$0.00'

def test_format_date():
    """Test date formatting"""
    # Test with date object
    date = datetime(2023, 1, 15).date()
    assert format_date(date) == '2023-01-15'
    
    # Test with datetime object
    dt = datetime(2023, 1, 15, 10, 30, 0)
    assert format_date(dt) == '2023-01-15'
    
    # Test with string date
    assert format_date('2023-01-15') == '2023-01-15'
    
    # Test with custom format
    assert format_date(date, format_str='%d/%m/%Y') == '15/01/2023'
    assert format_date(dt, format_str='%b %d, %Y') == 'Jan 15, 2023'
    
    # Test with None
    assert format_date(None) == ''
    
    # Test with empty string
    assert format_date('') == ''
    
    # Test with invalid string format (should return the original)
    assert format_date('not-a-date') == 'not-a-date'

def test_truncate_text():
    """Test text truncation"""
    # Test basic truncation
    long_text = 'This is a long text that should be truncated at some point.'
    assert truncate_text(long_text, max_length=20) == 'This is a long...'
    
    # Test text shorter than max length
    short_text = 'Short text'
    assert truncate_text(short_text, max_length=20) == 'Short text'
    
    # Test with custom suffix
    assert truncate_text(long_text, max_length=20, suffix='...more') == 'This is a long...more'
    
    # Test with None
    assert truncate_text(None) == ''
    
    # Test with empty string
    assert truncate_text('') == '' 