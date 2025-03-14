# AKC CRM

## ⚠️ IMPORTANT DEPLOYMENT NOTICE ⚠️

**DO NOT DELETE THE `DEPLOYMENT_README.md` FILE**

This project has a specific deployment configuration that is documented in the `DEPLOYMENT_README.md` file. This file contains the only verified working deployment method for this application.

## About

AKC CRM is a customer relationship management system for Austin Kunz Construction. It provides tools for managing clients, projects, and documents.

## Deployment

For deployment instructions, please refer to the `DEPLOYMENT_README.md` file. Do not attempt to deploy this application using any other method, as it may result in deployment failures and service outages.

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

## Project Structure

The current simplified project structure is:

```
akc-crm/
├── app.py                # Main application entry point
├── requirements-minimal.txt  # Minimal Python dependencies
├── Dockerfile            # Container configuration
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── DEPLOYMENT_README.md  # Critical deployment documentation
└── README.md             # Project documentation
```

## API Endpoints

The API provides the following endpoints:

- `/`: Main application homepage
- `/health`: Health check endpoint

For detailed API documentation, visit the `/docs` endpoint when the server is running.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
