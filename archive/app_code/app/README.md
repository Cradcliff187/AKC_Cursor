# AKC LLC Construction CRM

This application is a Construction Customer Relationship Management system for AKC LLC. It provides a comprehensive platform for managing projects, clients, vendors, tasks, time tracking, documents, and reporting.

## Code Standards and Structures

This project follows several standardized patterns defined in the JSON guides:

### 1. Database Schema Structure

Our database schema and service modules follow the structure defined in `Backend JSON.json`, with proper naming conventions for tables and columns. For example:

- Project IDs use the `projectid` field format
- Foreign keys follow the convention `customerid` referencing `customers.customerid`
- All tables include `created_at` and `updated_at` timestamps

### 2. File Storage Structure

Document management follows the folder structure defined in `File Storage Structure.json`:

```
{CustomerID}-{ProjectID}-{ProjectName}/
  ├── Estimates/
  ├── Materials/
  └── SubInvoices/
```

For example, a project folder might be: `CUST001-PROJ123-MainOfficeRenovation/`

### 3. ID Pattern Generation

Entity IDs follow structured patterns with prefixes:

- Projects: `PROJ-XXXXXXXX` (e.g., `PROJ-A3B4C5D6`)
- Customers: `CUST-XXXXXXXX` (e.g., `CUST-12345678`)
- Vendors: `VEND-XXXXXXXX`
- Tasks: `TASK-XXXXXXXX`
- Documents: `DOC-XXXXXXXX`
- Time Entries: `TIME-XXXXXXXX`

### 4. Statuses and Transitions

The application implements the status values and transition rules defined in `Statues and Transitions.json`:

#### Project Statuses:
- `PENDING`: Initial state when project is created
- `APPROVED`: Project is approved but work hasn't started
- `IN_PROGRESS`: Work is actively being done
- `COMPLETED`: Work is finished
- `CANCELED`: Project was canceled

#### Status Transitions:
Each status can only transition to specific valid states. For example, a `PENDING` project can only transition to `APPROVED` or `CANCELED`.

## Implementation Details

### Service Modules

The application uses service modules to interact with the database:

- `projects.py`: Manages project data and enforces status transitions
- `tasks.py`: Handles task creation, updates, and status management
- `documents.py`: Manages document uploads following the folder structure
- `time.py`: Tracks time entries for projects and tasks
- `utils.py`: Provides utility functions for ID generation and other shared operations

### Status Validation

Status transitions are validated using the rules defined in the guides. Invalid transitions are rejected with error messages.

### Mock Data

During development, the application can operate with mock data when the Supabase backend is unavailable. All mock data follows the same structure as the real database.

## Development

To run the application in development mode:

```
python run.py
```

The server will start at http://127.0.0.1:5000 with debug mode enabled. 