from supabase import create_client
from flask import current_app, g
import os

def get_supabase():
    """Get or create Supabase client."""
    if 'supabase' not in g:
        supabase_url = current_app.config['SUPABASE_URL']
        supabase_key = current_app.config['SUPABASE_KEY']
        g.supabase = create_client(supabase_url, supabase_key)
    return g.supabase

def close_supabase(e=None):
    """Remove supabase client from g."""
    g.pop('supabase', None)

def init_app(app):
    """Register Supabase functions with the Flask app."""
    app.teardown_appcontext(close_supabase)
    
    # Load Supabase configuration
    app.config.update(
        SUPABASE_URL=os.getenv('SUPABASE_URL'),
        SUPABASE_KEY=os.getenv('SUPABASE_KEY')
    ) 