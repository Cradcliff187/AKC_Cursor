#!/bin/bash

# Set the project ID
PROJECT_ID="akc-crm"

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
gcloud config set run/region us-east4

echo "Initial setup complete!"
echo "Next steps will include:"
echo "1. Setting up Cloud Storage bucket"
echo "2. Configuring Secret Manager"
echo "3. Setting up Cloud Run service" 