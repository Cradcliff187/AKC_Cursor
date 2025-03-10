# Construction CRM

A comprehensive Construction Project Management System built with Flask and Supabase.

## Project Structure

```
construction-crm/
├── app/                    # Main application package
│   ├── models/             # Data models
│   ├── routes/             # Route handlers
│   ├── services/           # Database and external services
│   ├── static/             # Static assets (CSS, JS, images)
│   ├── templates/          # HTML templates
│   └── utils/              # Utility functions
├── instance/               # Instance-specific files
├── uploads/                # User uploaded files
├── .env                    # Environment variables (not in version control)
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore file
├── init_db.py              # Database initialization script
├── init_db.sql             # SQL schema
├── install.sh              # Installation script
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

## Features

- Project Management
- Client Management
- Vendor Management
- Subcontractor Management
- Document Management
- Task Management
- Time Tracking
- Reporting

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/construction-crm.git
   cd construction-crm
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the example environment file and update it with your settings:
   ```
   cp .env.example .env
   ```

5. Initialize the database:
   ```
   python init_db.py
   ```

6. Run the application:
   ```
   python run.py
   ```

## Environment Variables

Create a `.env` file with the following variables:

```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Deployment to Google Cloud Platform

### Prerequisites

1. Google Cloud Platform account
2. Google Cloud CLI installed locally
3. Docker installed locally (for testing)

### Deployment Steps

1. Authenticate with Google Cloud:
   ```
   gcloud auth login
   ```

2. Run the setup script for Google Cloud:
   ```
   chmod +x setup_gcloud.sh
   ./setup_gcloud.sh
   ```

3. Deploy to Cloud Run using Cloud Build:
   ```
   gcloud builds submit
   ```

4. Configure environment variables in Google Cloud Secret Manager (as shown in the setup script).

### Testing Locally with Docker

1. Build the Docker image:
   ```
   docker build -t akc-crm .
   ```

2. Run the container locally:
   ```
   docker run -p 8080:8080 akc-crm
   ```

3. Visit http://localhost:8080 to test the application.

### CI/CD Setup

This project is configured for continuous deployment using GitHub and Google Cloud Build:

1. Connect your GitHub repository to Google Cloud Build.
2. Configure the build trigger to use the cloudbuild.yaml in this repository.
3. Push changes to your main branch to trigger automatic deployments.

---

© 2023 AKC LLC. All Rights Reserved.
