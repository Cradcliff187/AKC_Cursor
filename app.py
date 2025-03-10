import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable for Cloud Run
    port = int(os.environ.get('PORT', 8080))
    # Use 0.0.0.0 to listen on all interfaces
    app.run(host='0.0.0.0', port=port, debug=False) 