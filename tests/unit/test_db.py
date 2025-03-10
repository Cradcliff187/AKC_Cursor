"""
Unit tests for database functions
"""
import pytest
import sqlite3
from app.db import get_db, close_db, init_db

def test_get_db(app):
    """Test that get_db returns a database connection"""
    with app.app_context():
        db = get_db()
        assert db is get_db()  # Test connection reuse within context
        assert isinstance(db, sqlite3.Connection)
        
        # Test row factory is set correctly
        cursor = db.execute('SELECT 1 AS test')
        row = cursor.fetchone()
        assert hasattr(row, 'keys')
        assert row['test'] == 1

def test_close_db(app):
    """Test that database connection is closed after context"""
    with app.app_context():
        db = get_db()
        
    # Connection should now be closed
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    
    assert 'closed database' in str(e.value)

def test_init_db_command(app, monkeypatch):
    """Test init_db_command function"""
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('app.db.init_db', fake_init_db)
    
    with app.app_context():
        from app.db import init_db_command
        # Patch the click.command decorator to run the function directly
        runner = app.test_cli_runner()
        result = runner.invoke(init_db_command)
        assert 'Initialized the database.' in result.output
        assert Recorder.called 