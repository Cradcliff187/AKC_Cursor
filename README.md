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

# AKC Construction CRM

A comprehensive Construction CRM system for managing clients, projects, invoices, bids, and more.

## Overview

AKC Construction CRM is a full-featured customer relationship management system designed specifically for construction companies. It provides tools for managing clients, projects, invoices, bids, expenses, time tracking, and document management.

## Features

- **User Management**: Create and manage user profiles with different roles and permissions
- **Client Management**: Track client information, contacts, and interactions
- **Project Management**: Manage construction projects, tasks, and timelines
- **Financial Management**: Create and track invoices, payments, and expenses
- **Bid Management**: Create, send, and track bids and proposals
- **Time Tracking**: Track employee time on projects and tasks
- **Document Management**: Store and manage project documents and files
- **Reporting**: Generate reports on project status, financials, and more

## Tech Stack

- **Backend**: Python with FastAPI
- **Database**: PostgreSQL with Supabase
- **Authentication**: Supabase Auth
- **Frontend**: React with Material-UI (separate repository)

## Supabase Integration

The application uses Supabase for database storage, authentication, and file storage. The integration includes:

- **Authentication**: User registration, login, and session management using Supabase Auth
- **Database**: PostgreSQL database with Row-Level Security (RLS) policies for data protection
- **Storage**: File storage for project documents and attachments
- **Real-time**: Real-time updates for collaborative features

### Supabase Setup

To set up Supabase for this application:

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Copy your Supabase URL and API keys to the `.env` file
3. Run the setup script to create tables and apply RLS policies:
   ```
   python setup_supabase.py
   ```
4. Verify the setup with:
   ```
   python check_supabase.py
   ```

## Deployment to Google Cloud Run

The application is designed to be deployed to Google Cloud Run, a fully managed platform for containerized applications.

### Prerequisites

- Google Cloud account with billing enabled
- Google Cloud SDK installed and configured
- Docker installed locally (for testing)

### Deployment Steps

1. **Set up Google Cloud Project**:
   - Create a new project or use an existing one
   - Enable the Cloud Run API
   - Set up a service account with appropriate permissions

2. **Set up Google Cloud Secrets**:
   - Create secrets for sensitive environment variables:
     ```
     gcloud secrets create SUPABASE_URL --data-file=- <<< "your-supabase-url"
     gcloud secrets create SUPABASE_ANON_KEY --data-file=- <<< "your-supabase-anon-key"
     gcloud secrets create SUPABASE_SERVICE_ROLE_KEY --data-file=- <<< "your-supabase-service-role-key"
     gcloud secrets create SUPABASE_DB_PASSWORD --data-file=- <<< "your-supabase-db-password"
     gcloud secrets create FLASK_SECRET_KEY --data-file=- <<< "your-flask-secret-key"
     ```

3. **Deploy to Google Cloud Run**:
   - Use the provided deployment script:
     ```
     ./deploy.sh
     ```
   - Or deploy manually:
     ```
     gcloud run deploy akc-crm \
       --source . \
       --platform managed \
       --region us-east4 \
       --allow-unauthenticated \
       --set-secrets=SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_ANON_KEY:latest,SUPABASE_SERVICE_ROLE_KEY=SUPABASE_SERVICE_ROLE_KEY:latest,SUPABASE_DB_PASSWORD=SUPABASE_DB_PASSWORD:latest,FLASK_SECRET_KEY=FLASK_SECRET_KEY:latest
     ```

4. **Verify Deployment**:
   - Access the deployed API at the provided URL
   - Test the API endpoints using the provided test script:
     ```
     python test_api.py --url https://your-cloud-run-url.run.app
     ```

### Continuous Deployment

For continuous deployment, you can set up a Cloud Build trigger to automatically deploy the application when changes are pushed to the repository.

1. **Set up Cloud Build**:
   - Enable the Cloud Build API
   - Connect your repository to Cloud Build
   - Create a trigger for automatic deployments

2. **Configure Cloud Build**:
   - Use the provided `cloudbuild.yaml` file for build configuration
   - Set up appropriate IAM permissions for Cloud Build service account

## Project Status

We've identified and resolved several issues with the database setup:

1. **Missing Tables**: The following tables were missing from the Supabase database:
   - user_notifications
   - project_tasks
   - payments

2. **Schema Issues**: The `user_profiles` table exists but doesn't have the required `auth_id` column that our application expects.

3. **Missing Functions**: The following PostgreSQL functions were missing:
   - `exec_sql` - Used for executing dynamic SQL queries
   - `update_updated_at_column` - Used for automatically updating the `updated_at` column when records are modified

## Setup Instructions

To fix these issues and set up the database correctly, follow the instructions in `supabase_setup_instructions.md`. The key steps are:

1. Create the `exec_sql` function in Supabase
2. Fix the `user_profiles` table schema
3. Create the missing tables
4. Verify that all tables and functions exist

## Testing

After completing the setup, you can test the database connection by running:

```
python test_db_connection.py
```

This script will:
- Test the connection to the Supabase database
- Check if all required tables exist
- Test basic operations with the UserProfileService

## Test Data

1. To populate the database with test data, run:
   ```
   python insert_all_test_data.py
   ```
2. This will create sample records in all tables with proper relationships.
3. See `test_data_summary.md` for details about the test data.

## Running the Application

Once the setup is complete, you can run the application with:

```
python run_app.py
```

The API will be available at `http://localhost:8000` and the API documentation will be available at `http://localhost:8000/docs`.

## Project Structure

```
akc-construction-crm/
├── api/                  # API routes and endpoints
├── models/               # Data models
├── services/             # Business logic and database services
├── tests/                # Unit and integration tests
├── app.py                # Main application entry point
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## API Endpoints

The API provides the following endpoints:

- `/api/users`: User profile management
- `/api/clients`: Client management
- `/api/projects`: Project management
- `/api/invoices`: Invoice management
- `/api/bids`: Bid management
- `/api/expenses`: Expense management
- `/api/time-entries`: Time tracking
- `/api/documents`: Document management

For detailed API documentation, visit the `/docs` endpoint when the server is running.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Next Steps

After setting up the database, the next steps would be:

1. Implement the remaining service layer methods
2. Create API endpoints for the various resources
3. Develop the frontend UI
4. Implement authentication and authorization
5. Add unit and integration tests
