# Static Assets Directory

This directory contains all static assets for the AKC CRM application, including CSS, JavaScript, images, and fonts.

## Directory Structure

```
static/
├── css/              # Stylesheets
│   ├── bootstrap.min.css           # Bootstrap framework
│   ├── fontawesome.min.css         # Font Awesome icons
│   └── custom.css                  # Custom application styles
├── js/               # JavaScript files
│   ├── bootstrap.bundle.min.js     # Bootstrap with Popper.js
│   ├── jquery.min.js               # jQuery library
│   ├── chart.min.js                # Chart.js for data visualization
│   └── app.js                      # Custom application scripts
├── img/              # Images
│   ├── logo.png                    # Application logo
│   ├── favicon.ico                 # Favicon
│   └── backgrounds/                # Background images
├── fonts/            # Custom fonts
└── uploads/          # Uploaded files (documents, etc.)
    ├── projects/                   # Project documents
    ├── invoices/                   # Invoice attachments
    └── tmp/                        # Temporary uploads
```

## Key Files

### CSS

- **bootstrap.min.css**: Main styling framework for the application
- **custom.css**: Custom styles that override Bootstrap defaults and add application-specific styling

### JavaScript

- **app.js**: Main application scripts including:
  - Form validation
  - Dynamic UI interactions
  - AJAX requests for dynamic content
  - Chart and report rendering

### Images

- **logo.png**: Application logo used in the navigation bar and login screen
- Various UI elements and icons

## Uploading Files

The `uploads/` directory is used for storing user-uploaded files:
- Files are organized by entity type (projects, invoices, etc.)
- File names are prefixed with timestamps to prevent collisions
- Original file extensions are preserved
- These files are served directly by the application via the `/documents/{document_id}` route

## Asset Management

Static assets are loaded in templates using the `url_for('static', filename='path/to/file')` function to ensure proper URL generation. 