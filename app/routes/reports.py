from flask import (
    Blueprint, flash, redirect, render_template, 
    request, session, url_for, jsonify
)
from app.routes.auth import login_required

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
def show_reports():
    # Mock report data for development
    report_data = {
        'client_stats': {
            'total_clients': 8,
            'clients_with_projects': 6,
            'avg_projects_per_client': 2.5
        },
        'budget_stats': {
            'total_budget': 750000.00,
            'total_spent': 450000.00,
            'avg_project_budget': 125000.00,
            'avg_project_spent': 75000.00
        },
        'status_stats': {
            'Planning': 3,
            'In Progress': 6,
            'On Hold': 1,
            'Completed': 5
        },
        'status_counts': {
            'Planning': 3,
            'In Progress': 6,
            'On Hold': 1,
            'Completed': 5
        },
        'monthly_data': {
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'revenue': [45000, 52000, 49000, 58000, 63000, 68000],
            'expenses': [32000, 38000, 42000, 43000, 47000, 48000],
            'projects_started': [2, 3, 1, 2, 4, 3],
            'projects_completed': [1, 2, 2, 1, 3, 2],
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'new_projects': [2, 3, 1, 2, 4, 3],
            'completed_projects': [1, 2, 2, 1, 3, 2],
            'revenue': [45000, 52000, 49000, 58000, 63000, 68000]
        },
        'projects': [
            {
                'id': 1,
                'name': 'Residential Renovation',
                'client': 'John Smith',
                'client_id': 1,
                'status': 'In Progress',
                'budget': 120000.00,
                'budget_spent': 85000.00
            },
            {
                'id': 2,
                'name': 'Commercial Office Remodel',
                'client': 'ABC Corporation',
                'client_id': 2,
                'status': 'Planning',
                'budget': 250000.00,
                'budget_spent': 75000.00
            },
            {
                'id': 3,
                'name': 'Kitchen Remodel',
                'client': 'Sarah Johnson',
                'client_id': 3,
                'status': 'Completed',
                'budget': 45000.00,
                'budget_spent': 47500.00
            },
            {
                'id': 4,
                'name': 'Bathroom Renovation',
                'client': 'Michael Davis',
                'client_id': 4,
                'status': 'In Progress',
                'budget': 35000.00,
                'budget_spent': 28000.00
            },
            {
                'id': 5,
                'name': 'Deck Construction',
                'client': 'Robert Wilson',
                'client_id': 5,
                'status': 'In Progress',
                'budget': 18000.00,
                'budget_spent': 12000.00
            }
        ],
        'clients': [
            {'id': 1, 'name': 'John Smith'},
            {'id': 2, 'name': 'ABC Corporation'},
            {'id': 3, 'name': 'Sarah Johnson'},
            {'id': 4, 'name': 'Michael Davis'},
            {'id': 5, 'name': 'Robert Wilson'},
            {'id': 6, 'name': 'XYZ Company'},
            {'id': 7, 'name': 'Jennifer Taylor'},
            {'id': 8, 'name': 'David Brown'}
        ]
    }
    
    return render_template('reports.html', report_data=report_data) 