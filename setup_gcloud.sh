#!/bin/bash

# Set the project ID
PROJECT_ID="akc-crm"
REGION="us-east4"
STORAGE_BUCKET="${PROJECT_ID}-storage"

# Configure gcloud to use the project
gcloud config set project $PROJECT_ID

# Enable necessary APIs
echo "Enabling necessary Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    storage.googleapis.com \
    containerregistry.googleapis.com

# Set default region
gcloud config set run/region $REGION

# Create Cloud Storage bucket
echo "Creating Cloud Storage bucket..."
gsutil mb -l $REGION gs://$STORAGE_BUCKET

# Set up Secret Manager secrets
echo "Setting up Secret Manager secrets..."
# Read from .env file if it exists, otherwise prompt for values
if [ -f .env ]; then
    source .env
else
    echo "No .env file found. Please enter the required values:"
    read -p "SUPABASE_URL: " SUPABASE_URL
    read -p "SUPABASE_KEY: " SUPABASE_KEY
    read -p "SUPABASE_SERVICE_KEY: " SUPABASE_SERVICE_KEY
    read -p "SUPABASE_DB_PASSWORD: " SUPABASE_DB_PASSWORD
    read -p "FLASK_SECRET_KEY: " SECRET_KEY
fi

# Create secrets
echo "Creating secrets in Secret Manager..."
echo -n "${SUPABASE_URL}" | gcloud secrets create SUPABASE_URL --data-file=-
echo -n "${SUPABASE_KEY}" | gcloud secrets create SUPABASE_KEY --data-file=-
echo -n "${SUPABASE_SERVICE_KEY}" | gcloud secrets create SUPABASE_SERVICE_KEY --data-file=-
echo -n "${SUPABASE_DB_PASSWORD}" | gcloud secrets create SUPABASE_DB_PASSWORD --data-file=-
echo -n "${SECRET_KEY}" | gcloud secrets create FLASK_SECRET_KEY --data-file=-

echo "Cloud setup complete!"
echo "Next steps:"
echo "1. Deploy your application using: gcloud builds submit"
echo "2. Your application will be available at: https://akc-crm-<hash>.a.run.app" 