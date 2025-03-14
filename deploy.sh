#!/bin/bash

# Exit on error
set -e

# Function to check if running on Windows
is_windows() {
    case "$(uname -s)" in
        CYGWIN*|MINGW*|MSYS*)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        echo "Error: gcloud CLI is not installed. Please install it first."
        echo "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
}

# Function to check if user is authenticated
check_auth() {
    if ! gcloud auth print-identity-token &> /dev/null; then
        echo "Error: Not authenticated with gcloud. Please run 'gcloud auth login' first."
        exit 1
    fi
}

# Function to check if project is set
check_project() {
    if [ -z "$(gcloud config get-value project)" ]; then
        echo "Error: No project set. Please run 'gcloud config set project YOUR_PROJECT_ID' first."
        exit 1
    fi
}

# Main deployment function
deploy() {
    echo "Starting deployment process..."
    
    # Check prerequisites
    check_gcloud
    check_auth
    check_project
    
    # Set variables
    SERVICE_NAME="akc-crm"
    REGION="us-east4"
    
    echo "Deploying to Google Cloud Run..."
    
    # Deploy the service
    gcloud run deploy $SERVICE_NAME \
        --source . \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-secrets=SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_ANON_KEY:latest,SUPABASE_SERVICE_ROLE_KEY=SUPABASE_SERVICE_ROLE_KEY:latest,SUPABASE_DB_PASSWORD=SUPABASE_DB_PASSWORD:latest,FLASK_SECRET_KEY=FLASK_SECRET_KEY:latest \
        --set-env-vars="FASTAPI_ENV=production"
    
    echo "Deployment completed successfully!"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')
    echo "Service URL: $SERVICE_URL"
    
    # Test the deployment
    echo "Testing deployment..."
    echo "Checking API health at $SERVICE_URL/health"
    curl -s $SERVICE_URL/health
    echo ""
    
    echo "Deployment and testing completed successfully!"
}

# Run deployment
deploy 