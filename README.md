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

---

© 2023 AKC LLC. All Rights Reserved.
