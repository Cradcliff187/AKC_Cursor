# This file exists for compatibility with the Dockerfile
# We're now using run.py as the main entry point

from run import app

if __name__ == '__main__':
    # This won't be used by Gunicorn, but is here for compatibility
    # with directly running this file
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False) 