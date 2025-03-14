from flask import Flask, g, request, session
from dotenv import load_dotenv
import os
import re
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

def nl2br(value):
    """Convert newlines to <br> tags for Jinja templates"""
    if not value:
        return ""
    value = value.replace('\r\n', '<br>')  # Handle Windows-style newlines first
    value = value.replace('\n', '<br>')    # Then handle Unix-style newlines
    return value

def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Load environment variables
    load_dotenv()
    
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        SUPABASE_URL=os.getenv('SUPABASE_URL'),
        SUPABASE_KEY=os.getenv('SUPABASE_KEY'),
        SUPABASE_SERVICE_ROLE_KEY=os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
        SUPABASE_DB_PASSWORD=os.getenv('SUPABASE_DB_PASSWORD'),
        ENV=os.getenv('FLASK_ENV', 'production')
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ensure the upload folder exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass
    
    # Register the database commands
    from . import db
    db.init_app(app)
    
    # Initialize Supabase client
    from . import supabase_client
    supabase_client.init_app(app)
    
    # Register blueprints
    from .routes import main, auth, clients, projects, bids, invoices, documents
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(clients.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(bids.bp)
    app.register_blueprint(invoices.bp)
    app.register_blueprint(documents.bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return 'Page not found', 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        import traceback
        error_message = str(e)
        stack_trace = traceback.format_exc()
        
        # Log the error
        app.logger.error(f"Internal Server Error: {error_message}")
        app.logger.error(f"Stack Trace: {stack_trace}")
        
        # Only show detailed errors in development
        if app.config['ENV'] == 'development':
            error_details = f"""
            <h1>Internal Server Error</h1>
            <p>An error occurred while processing your request:</p>
            <pre>{error_message}</pre>
            <h2>Stack Trace:</h2>
            <pre>{stack_trace}</pre>
            """
            return error_details, 500
        else:
            return 'Internal Server Error. Our team has been notified.', 500
            
    # Custom error handler for Supabase connection issues
    @app.errorhandler(Exception)
    def handle_exception(e):
        if 'supabase' in str(e).lower() or 'connection' in str(e).lower():
            app.logger.error(f"Supabase Connection Error: {str(e)}")
            
            # Only show detailed errors in development
            if app.config['ENV'] == 'development':
                return f"""
                <h1>Database Connection Error</h1>
                <p>There was a problem connecting to the database:</p>
                <pre>{str(e)}</pre>
                <p>Please check your Supabase connection settings.</p>
                """, 500
            else:
                return 'Service temporarily unavailable. Please try again later.', 503
                
        # For other exceptions, fall back to default handlers
        return app.handle_http_exception(e) if hasattr(e, 'code') else internal_server_error(e)
    
    # Register Jinja2 filters
    app.jinja_env.filters['nl2br'] = nl2br
    
    return app
