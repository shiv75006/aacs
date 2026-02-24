"""
Passenger WSGI entry point for cPanel deployment.
This file is required for cPanel's Passenger to run FastAPI.
"""
import sys
import os

# Add the application directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI app
from app.main import app

# Passenger expects an 'application' callable
application = app
