# AKC CRM Application

A comprehensive CRM system for AKC Construction, built with FastAPI, Jinja2 templates, and Supabase.

## Brand Information

The AKC CRM application follows the official AKC LLC brand guidelines. For detailed information on logo usage, color palette, typography, and UI components, please refer to:

- [Brand Guidelines](BRAND_GUIDELINES.md)

## Project Structure

```
AKC-CRM/
├── app.py                 # Main application file with FastAPI app initialization
├── dependencies.py        # Shared dependencies and utilities
├── mock_data.py           # Mock data for development/testing
├── routes/                # API routes organized by feature
│   ├── __init__.py        # Package initialization
│   ├── auth.py            # Authentication routes
│   ├── contacts.py        # Contact management routes
│   ├── customers.py       # Customer management routes
│   ├── documents.py       # Document management routes
│   ├── expenses.py        # Expense tracking routes
│   ├── invoices.py        # Invoice management routes
│   ├── projects.py        # Project management routes
│   ├── reports.py         # Reporting routes
│   ├── time_logs.py       # Time tracking routes
│   └── vendors.py         # Vendor management routes
├── static/                # Static assets (CSS, JS, images)
│   ├── css/               # Stylesheets including brand styling
│   ├── js/                # JavaScript files
│   └── img/               # Images including the logo
└── templates/             # Jinja2 HTML templates
    ├── components/        # Reusable UI components
    └── reports/           # Report-specific templates
```

## Key Components

### 1. Router Files (routes/*.py)

Each feature has its own router file following a standard pattern:
- All routes use authentication checks via `check_auth(session)`
- Error handling wraps all database operations
- Routes return HTML responses via Jinja2 templates
- Each file has its own APIRouter instance that's imported in app.py

### 2. Templates (templates/*.html)

Templates follow these conventions:
- All extend from base.html
- Use the `url_for()` function for generating URLs
- Use Bootstrap 5 for styling with AKC brand overrides
- Forms use POST methods with proper CSRF protection

### 3. Data Flow

1. Route handlers check authentication
2. Data is fetched from Supabase or mock data
3. Data is processed/filtered as needed
4. Templates are rendered with the processed data

### 4. URL Conventions

URLs follow RESTful conventions:
- List routes: `/entity` (e.g., `/projects`)
- Detail routes: `/entity/{id}` (e.g., `/projects/123`)
- Creation forms: `/entity/new`
- Edit forms: `/entity/{id}/edit`
- Delete actions: `/entity/{id}/delete`
- Status updates: `/entity/{id}/status`

## Brand Implementation

The AKC brand has been implemented through:

1. **Custom CSS**: `static/css/akc-brand.css` contains all brand-specific styling
2. **Logo Integration**: Logo placed in the navbar with proper sizing and spacing
3. **Typography**: Montserrat and Open Sans fonts for consistent text styling
4. **Color Scheme**: AKC blue (#0485ea) used consistently throughout the UI
5. **Interactive Elements**: Subtle animations and transitions for a polished feel

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see .env.example)
4. Run the application: `uvicorn app:app --reload`

## Deployment

See DEPLOYMENT_README.md for detailed deployment instructions for Google Cloud.

## About

- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5 framework
- **Backend**: Python FastAPI framework
- **Database**: PostgreSQL database with Row-Level Security (RLS) policies for data protection
- **Storage**: File storage for project documents and attachments

## API Endpoints

See the API documentation for details on available endpoints and their usage.

## Current Deployment

The application is currently deployed at:
https://akc-crm-988587667075.us-east4.run.app

## Development

For development purposes, you can run the application locally using:

```bash
python app.py
```

Make sure to install the dependencies from `requirements-minimal.txt`:

```bash
pip install -r requirements-minimal.txt
```

## Features

- **User Management**: Create and manage user profiles with different roles and permissions
- **Client Management**: Track client information, contacts, and interactions
- **Project Management**: Manage construction projects, tasks, and timelines
- **Financial Management**: Create and track invoices, payments, and expenses
- **Bid Management**: Create, send, and track bids and proposals
- **Document Management**: Store and manage project documents and files

## Tech Stack

- **Backend**: Python with FastAPI
- **Database**: PostgreSQL with Supabase
- **Authentication**: Supabase Auth
- **Frontend**: HTML/CSS with Bootstrap (templates directory)

## Supabase Integration

The application uses Supabase for database storage, authentication, and file storage. The integration includes:

- **Authentication**: User registration, login, and session management using Supabase Auth
- **Database**: PostgreSQL database with Row-Level Security (RLS) policies for data protection
- **Storage**: File storage for project documents and attachments

## API Endpoints

The API provides the following endpoints:

- `/`: Main application homepage
- `/health`: Health check endpoint

For detailed API documentation, visit the `/docs` endpoint when the server is running.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
