#!/usr/bin/env python3
"""
Run script for Business Flask Application
"""
import os
import sys

# Add parent directory to path to access shared modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(parent_dir, 'shared'))

from app import business_app

if __name__ == '__main__':
    print("Starting KathaPe Business Application...")
    print("Business app will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop the application")
    
    # Run the business app
    business_app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5001)),
        threaded=True
    )
