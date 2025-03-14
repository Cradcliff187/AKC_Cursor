from supabase import create_client, Client
from flask import current_app, g
import os

def get_supabase() -> Client:
    """Get a Supabase client instance."""
    # Get configuration from Flask app
    url = current_app.config.get('SUPABASE_URL')
    key = current_app.config.get('SUPABASE_KEY')
    
    # Create and return the client
    return create_client(url, key)

def close_supabase():
    """Close the Supabase client connection."""
    # No explicit close needed for this version
    pass

def init_app(app):
    """Initialize Supabase client with the Flask app."""
    # Register teardown function
    @app.teardown_appcontext
    def teardown_supabase(exception):
        close_supabase()
    
    # Load Supabase configuration
    app.config.update(
        SUPABASE_URL=os.getenv('SUPABASE_URL'),
        SUPABASE_KEY=os.getenv('SUPABASE_KEY')
    ) 