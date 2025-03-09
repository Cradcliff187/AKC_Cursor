# Construction CRM Flask Application

A simple Construction CRM built with Flask to help construction companies manage their projects.

## Features

- Project dashboard
- Project detail view
- Responsive design with Bootstrap 5

## Requirements

- Python 3.7+
- Flask
- Werkzeug
- Jinja2
- python-dotenv

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd construction-crm
```

2. Create a virtual environment and activate it:
```
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Set up environment variables:
Copy the `.env.example` to `.env` and set your configuration variables.

## Running the Application

1. Start the Flask development server:
```
flask run
```

2. Visit `http://127.0.0.1:5000/` in your web browser.

## Project Structure

- `app.py`: Main Flask application
- `templates/`: HTML templates
  - `base.html`: Base template with common elements
  - `index.html`: Project list page
  - `project_detail.html`: Project details page
- `static/`: Static assets
  - `css/`: CSS stylesheets
  - `js/`: JavaScript files

## Development

This is a simple Flask application for demonstration purposes. In a real-world implementation, you would want to:

- Add a database (e.g., SQLAlchemy with SQLite, PostgreSQL, or MySQL)
- Implement user authentication
- Add form validation
- Create a more robust project structure
