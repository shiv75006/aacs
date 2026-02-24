"""
Passenger WSGI entry point for cPanel deployment.
This file is required for cPanel's Passenger to run FastAPI.
"""
import sys
import os

# Add the application directory to the Python path
application_path = os.path.dirname(__file__)
sys.path.insert(0, application_path)

# Import the FastAPI app
from app.main import app as application

# For cPanel entry point "app"
app = application
