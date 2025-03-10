from flask import (
    Blueprint, flash, g, redirect, render_template, 
    request, session, url_for
)
from app.routes.auth import login_required
from app.services.projects import get_projects_by_user
from app.services.supabase import get_user_by_id, get_projects_by_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
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