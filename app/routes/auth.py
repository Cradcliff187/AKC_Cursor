from flask import (
    Blueprint, flash, g, redirect, render_template, 
    request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from app.services.supabase import get_user_by_email, authenticate_user

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        else:
            # Try to authenticate the user
            auth_result = authenticate_user(email, password)
            
            if auth_result is None:
                error = 'Invalid email or password.'
            else:
                # Authentication successful
                user = get_user_by_email(email)
                
                if user:
                    # Clear the session and add user info
                    session.clear()
                    session['user_id'] = user['id']
                    session['user_email'] = user['email']
                    session['user_name'] = f"{user.get('first_name', '')} {user.get('last_name', '')}"
                    
                    return redirect(url_for('main.dashboard'))
                else:
                    error = 'User not found in database.'

        if error:
            flash(error)

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/dev-login')
def dev_login():
    """Development-only route for quick login without authentication"""
    # Clear the session and add mock user info
    session.clear()
    session['user_id'] = 1
    session['user_email'] = 'admin@example.com'
    session['user_name'] = 'Admin User'
    
    return redirect(url_for('main.dashboard')) 