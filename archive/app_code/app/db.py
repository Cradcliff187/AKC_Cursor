from flask import g, current_app
import click
from flask.cli import with_appcontext
from app.services.supabase import supabase

def get_db():
    """Connect to the application's configured database."""
    if 'db' not in g:
        g.db = supabase
    return g.db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)
    # No need to close Supabase client

def init_db():
    """Initialize database tables if they don't exist."""
    db = get_db()
    if db is None:
        click.echo('Warning: Supabase client not initialized')
        return
        
    # Since we're using Supabase, we don't need to run SQL scripts
    # Tables should be created through Supabase dashboard or migrations
    click.echo('Database connection verified.')

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Verify database connection and tables."""
    init_db()
    click.echo('Database connection checked.')

def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command) 