from flask import Flask, g, request, session
from dotenv import load_dotenv
import os
import re
from flask_bootstrap import Bootstrap5

def nl2br(value):
    """Convert newlines to <br> tags for Jinja templates"""
    if not value:
        return ""
    return value.replace('\n', '<br>').replace('\r\n', '<br>')

def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Load environment variables
    load_dotenv()
    
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
    )

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        # Also create upload folder
        os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)
    except OSError:
        pass
        
    # Initialize Bootstrap
    bootstrap = Bootstrap5(app)
    
    # Add device detection and user context middleware
    @app.before_request
    def before_request():
        # Import here to avoid circular imports
        from app.services.user_context import is_mobile_device, get_user_role
        
        # Detect if the user is on a mobile device
        g.is_mobile = is_mobile_device()
        
        # Set the user's role
        g.user_role = get_user_role()
        
        # For development, allow role switching via query parameter
        if app.config.get('ENV') == 'development' and 'role' in request.args:
            new_role = request.args.get('role')
            valid_roles = ['field_worker', 'foreman', 'project_manager', 'admin']
            if new_role in valid_roles:
                session['user_role'] = new_role
                g.user_role = new_role
    
    # Add template filters
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        """Convert newlines to HTML line breaks"""
        if not s:
            return ""
        return s.replace('\n', '<br>')
    
    # Register blueprints
    from app.routes import auth, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    
    from app.routes import projects, clients, vendors, tasks, documents, time
    app.register_blueprint(projects.bp)
    app.register_blueprint(clients.bp)
    app.register_blueprint(vendors.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(documents.bp)
    app.register_blueprint(time.bp)
    
    # Register field-specific routes
    from app.routes import field
    app.register_blueprint(field.bp)
    
    # Make url_for('index') == url_for('main.index')
    app.add_url_rule('/', endpoint='index')
    
    return app
