from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-for-flask')

# Sample data (in a real app, this would come from a database)
projects = [
    {"id": 1, "name": "Residential Renovation", "client": "John Smith", "status": "In Progress"},
    {"id": 2, "name": "Commercial Building", "client": "ABC Corp", "status": "Planning"},
    {"id": 3, "name": "Kitchen Remodel", "client": "Jane Doe", "status": "Completed"}
]

@app.route('/')
def index():
    return render_template('index.html', projects=projects)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = next((p for p in projects if p["id"] == project_id), None)
    if project:
        return render_template('project_detail.html', project=project)
    flash('Project not found', 'error')
    return redirect(url_for('index'))

@app.route('/api/projects')
def get_projects():
    return jsonify(projects)

if __name__ == '__main__':
    app.run(debug=True) 