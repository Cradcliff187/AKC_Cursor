from flask import Flask, g, request, session
from dotenv import load_dotenv
import os
import re
from flask_bootstrap import Bootstrap5

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
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
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
    
    # Initialize Bootstrap
    bootstrap = Bootstrap5(app)
    
    # Add custom template filters
    app.jinja_env.filters['nl2br'] = nl2br
    
    # Register the database commands
    from . import db
    db.init_app(app)
    
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
        return 'Internal Server Error', 500
    
    return app
