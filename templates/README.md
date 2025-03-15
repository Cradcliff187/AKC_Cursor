# Templates Directory

This directory contains all the Jinja2 HTML templates for the AKC CRM application. The templates follow a consistent structure and naming convention.

## Template Structure

All templates extend from `base.html`, which provides:
- Common CSS and JavaScript imports
- Navigation bar
- Footer
- Flash message handling
- Basic page layout

## Template Naming Conventions

Templates are named following these patterns:

- **Entity Lists**: `{entity}.html` (e.g., `projects.html`, `customers.html`)
- **Entity Details**: `{entity}_detail.html` (e.g., `project_detail.html`, `customer_detail.html`) 
- **Forms**: `{entity}_form.html` (e.g., `project_form.html`, `customer_form.html`)
- **Reports**: `reports/{report_name}.html` (e.g., `reports/time_summary_report.html`)
- **Errors**: `error.html`

## Common Template Functions

Templates use these helper functions consistently:

- `url_for('route_name', param=value)` - Generates URLs for routes
- `status_icons[status]` - Maps status values to Font Awesome icons
- `project_status_classes[status]` - Maps status values to Bootstrap classes
- `status_styles[status]` - Maps status values to text color classes

## Form Conventions

Forms follow these conventions:
- POST method for data submission
- Form inputs named to match route parameter names
- Required fields marked with asterisk (*)
- Client-side validation where appropriate
- Server-side validation in route handlers

## Modal Conventions

Many templates use Bootstrap modals for:
- Confirmation dialogs (delete actions)
- Add/edit forms for related entities
- Quick view of details

## Component Organization

The `components/` directory contains reusable template components like:
- Navigation elements
- Cards
- Form fields
- Modals

## Special Templates

- `base.html` - The main layout template that all other templates extend
- `error.html` - Generic error page for displaying error messages
- `login.html` / `register.html` - Authentication forms
- `index.html` - The landing/home page 