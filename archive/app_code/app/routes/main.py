from flask import (
    Blueprint, flash, g, redirect, render_template, 
    request, session, url_for
)
from app.routes.auth import login_required
from app.services.projects import get_projects_by_user
from app.services.supabase import get_user_by_id, get_projects_by_user
from datetime import datetime
import json
from flask import current_app
from app.services.supabase import supabase

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main index page"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    # Get user information
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    # Get projects for this user
    projects = get_projects_by_user(user_id)
    
    # Get dashboard statistics
    stats = {
        'total_projects': len(projects),
        'active_projects': sum(1 for p in projects if p.get('status') == 'In Progress'),
        'completed_projects': sum(1 for p in projects if p.get('status') == 'Completed'),
        'overdue_tasks': 0  # Placeholder, would need to implement task query
    }
    
    return render_template('dashboard.html', 
                          user=user,
                          projects=projects,
                          stats=stats)

@bp.route('/health')
def health_check():
    """Health check endpoint to verify the application and Supabase connection are working."""
    health_data = {
        "status": "ok",
        "version": "1.0",
        "timestamp": str(datetime.now()),
        "environment": current_app.config['ENV'],
        "database": "unknown"
    }
    
    # Check Supabase connection
    try:
        # Simple query to verify database connection
        result = supabase.table('users').select('id').limit(1).execute()
        if hasattr(result, 'data'):
            health_data["database"] = "connected" 
            health_data["supabase_status"] = "ok"
        else:
            health_data["database"] = "error"
            health_data["supabase_status"] = "error: no data attribute"
    except Exception as e:
        health_data["status"] = "degraded"
        health_data["database"] = "error"
        health_data["supabase_status"] = f"error: {str(e)}"
    
    return json.dumps(health_data) 