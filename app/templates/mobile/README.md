# Mobile-Optimized Templates and Role-Based Architecture

This directory contains mobile-optimized templates designed specifically for field workers in construction. The implementation follows a role-based architecture pattern that delivers appropriate views based on both device type (mobile vs desktop) and user role (field worker vs administrative users).

## Directory Structure

```
mobile/
├── base.html          # Mobile-optimized base template with bottom navigation
├── field/             # Templates for field workers on mobile
│   ├── dashboard.html # Simple dashboard with task and time tracking info
│   ├── tasks.html     # Task list optimized for field workers
│   ├── quick_log.html # Simplified time entry form 
│   ├── timer.html     # Real-time timer for tracking work
│   ├── upload_photo.html  # Camera-enabled photo upload
│   ├── materials.html     # Materials tracking and requests
│   └── offline.html       # Offline mode indicator
└── admin/             # Templates for managers/admins on mobile
    ├── dashboard.html # Administrative dashboard for mobile
    └── ...            # Additional admin mobile views
```

## Key Features

### 1. Progressive Web App (PWA) Support

The mobile templates are designed to work as a Progressive Web App, which allows field workers to:

- Install the app on their home screen
- Use the app offline in remote construction sites
- Automatically sync data when connectivity returns
- Receive push notifications for important updates

### 2. Touch-Optimized UI

The mobile interface is specifically designed for touch interaction:

- Large touch targets (min 48px height)
- Bottom navigation for thumb-friendly access
- Swipe gestures for common actions
- Simplified forms with minimal required fields

### 3. Device-Specific Optimizations

- Camera integration for document scanning and photo documentation
- Geolocation for job site verification
- Responsive layouts that adapt to different screen sizes
- Battery-efficient background operations

### 4. Role-Based Rendering

Templates are served based on both device type and user role:

- Field workers on mobile see the simplified field interface
- Managers on mobile get more complete but mobile-optimized views
- Desktop users see the full interface appropriate to their role

## Implementation Details

### User Context Detection

The application detects the user's device and role through middleware in `app/services/user_context.py`:

```python
@app.before_request
def detect_device_type():
    # Set mobile flag based on User-Agent
    g.is_mobile = is_mobile_device()
    
    # Set user role
    g.user_role = get_user_role()
```

### Template Selection

Templates are rendered using the `render_appropriate_template` function, which selects the correct template based on device and role:

```python
def render_appropriate_template(template_name, **context):
    if is_field_level_user() and g.is_mobile:
        return render_template(f'mobile/field/{template_name}', **context)
    elif is_admin_level_user() and g.is_mobile:
        return render_template(f'mobile/admin/{template_name}', **context)
    elif is_admin_level_user():
        return render_template(f'desktop/admin/{template_name}', **context)
    else:
        return render_template(f'desktop/field/{template_name}', **context)
```

### Offline Support

The application includes a service worker (`static/js/service-worker.js`) that:

- Caches essential assets and data
- Provides an offline fallback page
- Queues form submissions when offline
- Syncs data when connectivity is restored

## Usage

To test the mobile interface during development:

1. Use the Device Emulation feature in your browser's developer tools
2. Append `?role=field_worker` to your URL to simulate a field worker's view
3. Toggle connectivity in dev tools to test offline functionality

## Accessibility Considerations

The mobile templates are designed with accessibility in mind:

- High contrast ratios for outdoor visibility
- Large, readable text
- Proper ARIA labels and roles
- Support for screen readers
- Alternative input methods

## Best Practices

When adding new features to the mobile interface:

1. Keep forms as simple as possible - field workers need quick entry methods
2. Test under poor connectivity conditions
3. Ensure all critical functions work offline
4. Use progressive enhancement - features should degrade gracefully
5. Optimize for battery life by minimizing background operations 