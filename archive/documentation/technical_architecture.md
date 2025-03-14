# AKC Construction CRM - Technical Architecture Overview

## 1. Application Structure

The application follows a modern architecture with:

- **FastAPI Backend**: The main `app.py` file sets up a FastAPI application with routes for users, clients, and projects.
- **Model-View-Controller Pattern**: 
  - Models in the `models/` directory define data structures
  - API routes in the `api/` directory handle HTTP requests
  - Services in the `app/services/` directory contain business logic

## 2. Database Connection (Supabase)

The application uses Supabase as its database and backend service:

- **Connection Setup**: The `app/services/supabase.py` file handles database connections using the Supabase Python client
- **Environment Variables**: Database credentials are stored in environment variables:
  - `SUPABASE_URL`: The URL of your Supabase instance
  - `SUPABASE_KEY`: The anonymous key for client-side operations
  - `SUPABASE_SERVICE_ROLE_KEY`: The service role key for admin operations
- **Data Models**: Each entity (client, project, user, etc.) has a corresponding model file in the `models/` directory

## 3. Deployment to Google Cloud Run

The application is deployed to Google Cloud Run using:

- **Dockerfile**: Defines how the application is containerized
  - Uses Python 3.9 slim as the base image
  - Copies only necessary files (app.py, requirements, static files, templates)
  - Installs dependencies from requirements.txt
  - Exposes port 8080 and runs the application

- **Deployment Script (deploy.sh)**: Automates the deployment process
  - Checks prerequisites (gcloud CLI, authentication, project setup)
  - Deploys to Google Cloud Run with the following parameters:
    - Service name: `akc-crm`
    - Region: `us-east4`
    - Platform: `managed`
    - Public access: `allow-unauthenticated`
    - Secrets: Sets up environment variables from Google Cloud Secret Manager

- **Manual Deployment Command**: When not using the script, you can deploy with:
  ```
  gcloud run deploy akc-crm --source . --platform managed --region us-east4 --allow-unauthenticated
  ```

## 4. Environment Configuration

The application uses environment variables for configuration:

- **Local Development**: Uses `.env` file with `python-dotenv`
- **Production**: Uses Google Cloud Secret Manager for sensitive values:
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `SUPABASE_SERVICE_KEY`
  - `SUPABASE_DB_PASSWORD`
  - `FLASK_SECRET_KEY`

## 5. Dependencies

Key dependencies include:

- **Web Framework**: FastAPI for the API, with Flask components for some parts
- **Database**: Supabase client and PostgreSQL adapter
- **Authentication**: JWT for token validation
- **Cloud Integration**: Google Cloud libraries
- **Development Tools**: Testing frameworks (pytest)

## 6. Testing and Verification

The application includes several testing and verification scripts:

- **Database Schema Verification**: Scripts to check if the database schema matches expectations
- **Test Data Insertion**: Scripts to populate the database with test data
- **Deployment Testing**: Scripts to verify successful deployment

## 7. Current Deployment

The application is currently deployed at:
```
https://akc-crm-988587667075.us-east4.run.app
```

## 8. Next Steps for Supabase Integration

To complete the Supabase integration:

1. **Schema Migration**: Ensure all database tables defined in the models are created in Supabase
2. **Authentication Flow**: Complete the JWT authentication flow with Supabase
3. **Data Access Patterns**: Update service files to use Supabase client for CRUD operations
4. **Row-Level Security**: Implement RLS policies in Supabase for data security
5. **Testing**: Verify all database operations work correctly with the Supabase backend 