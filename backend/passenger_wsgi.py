"""
Passenger WSGI entry point for cPanel deployment.
This file is required for cPanel's Passenger to run FastAPI.
"""
import sys
import os

# Add the application directory to the Python path
application_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, application_path)

# Set environment variables for production
os.environ.setdefault('ENVIRONMENT', 'production')

try:
    # Import the FastAPI app
    from app.main import app as application
    # For cPanel entry point "app"
    app = application
except Exception as e:
    # Fallback error app for debugging
    import traceback
    error_message = f"Application failed to start:\n{str(e)}\n\n{traceback.format_exc()}"
    
    def app(environ, start_response):
        status = '500 Internal Server Error'
        output = error_message.encode('utf-8')
        response_headers = [('Content-type', 'text/plain'),
                          ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
    
    application = app
