# Routes Directory

This directory contains all route handlers for the AKC CRM application, organized by feature. Each file follows a consistent pattern to make the codebase easy to maintain and understand.

## Router Pattern

Each router file follows this structure:

1. **Imports**: Standard imports from FastAPI and dependencies
2. **Router Definition**: Creates an `APIRouter` instance
3. **Route Definitions**: HTTP methods with path operations
4. **Authentication**: All protected routes check authentication with `check_auth(session)`
5. **Error Handling**: Try/except blocks with appropriate error responses
6. **Template Rendering**: Uses Jinja2 templates for HTML responses

## Standard Routes

Most feature modules implement these standard routes:

| Method | Path                     | Purpose                          | Response          |
|--------|--------------------------|----------------------------------|-------------------|
| GET    | /{entity}                | List all entities with filtering | HTML list page    |
| GET    | /{entity}/new            | Display creation form            | HTML form         |
| POST   | /{entity}/new            | Create new entity                | Redirect to list  |
| GET    | /{entity}/{id}           | View entity details              | HTML detail page  |
| GET    | /{entity}/{id}/edit      | Display edit form                | HTML form         |
| POST   | /{entity}/{id}/edit      | Update entity                    | Redirect to detail|
| POST   | /{entity}/{id}/delete    | Delete entity                    | Redirect to list  |

## Special Routes

Some modules have feature-specific routes:

- **projects.py**: Team member management, task management, status updates
- **invoices.py**: Payment recording, sending, cancellation
- **documents.py**: File upload/download handling
- **reports.py**: Data aggregation and filtering for reports

## Mock Data Usage

During development, routes use mock data from `mock_data.py`. In production, these will be replaced with Supabase database operations.

## Router Files

- **auth.py**: Authentication routes (login, logout, registration)
- **contacts.py**: Contact management
- **customers.py**: Customer management 
- **documents.py**: Document management
- **expenses.py**: Expense tracking
- **invoices.py**: Invoice management
- **projects.py**: Project management
- **reports.py**: Report generation
- **time_logs.py**: Time tracking
- **vendors.py**: Vendor management 