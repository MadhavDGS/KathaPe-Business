"""
Common utilities and configurations shared between customer and business Flask apps
"""
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory, make_response
import os
import uuid
import json
import traceback
import time
import requests
import socket
import threading
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv
import sys
import logging
import io
import base64
import qrcode
from PIL import Image

# Helper function to get current time in IST
def get_ist_now():
    """Get current datetime in Indian Standard Time (UTC+5:30)"""
    utc_now = datetime.utcnow()
    ist_offset = timedelta(hours=5, minutes=30)
    ist_now = utc_now + ist_offset
    return ist_now

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check if running on Render
RENDER_DEPLOYMENT = os.environ.get('RENDER', False)

# Appwrite Configuration
from appwrite_config import AppwriteConfig
from appwrite_utils import AppwriteDB

# Initialize Appwrite
appwrite_config = AppwriteConfig()
appwrite_db = AppwriteDB()

# Set environment variables from hardcoded values only if not already set
os.environ.setdefault('SECRET_KEY', 'fc36290a52f89c1c92655b7d22b198e4')
os.environ.setdefault('UPLOAD_FOLDER', 'static/uploads')

# On Render, configure optimized settings
if RENDER_DEPLOYMENT:
    print("RENDER MODE: Optimizing for improved performance")
    # Disable PIL completely to save memory
    Image = None
    qrcode = None
    
    # Aggressive performance settings for Render
    DB_RETRY_ATTEMPTS = 2
    DB_RETRY_DELAY = 1.0
    DB_QUERY_TIMEOUT = 30  # Increase timeout to prevent worker timeouts
    RENDER_QUERY_LIMIT = 10  # Limit number of results returned in queries
    RENDER_DASHBOARD_LIMIT = 5  # Limit items shown on dashboard
else:
    # Normal settings for development
    DB_RETRY_ATTEMPTS = 3
    DB_RETRY_DELAY = 1  # seconds
    DB_QUERY_TIMEOUT = 5  # seconds
    RENDER_QUERY_LIMIT = 50  # Higher limit for local development
    RENDER_DASHBOARD_LIMIT = 10  # Higher limit for local development

# Add request logging middleware
class RequestLoggerMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request_time = time.time()
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '')
        
        logger.info(f"REQUEST START: {method} {path}")
        
        def custom_start_response(status, headers, exc_info=None):
            duration = time.time() - request_time
            logger.info(f"REQUEST END: {method} {path} - Status: {status} - Duration: {duration:.3f}s")
            return start_response(status, headers, exc_info)
        
        try:
            return self.app(environ, custom_start_response)
        except Exception as e:
            logger.error(f"CRITICAL ERROR: {method} {path} - {str(e)}")
            logger.error(traceback.format_exc())
            custom_start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error - Khatape</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 20px; }}
                    h1 {{ color: #e74c3c; }}
                    .error-box {{ 
                        background-color: #f8d7da; 
                        border: 1px solid #f5c6cb; 
                        border-radius: 5px; 
                        padding: 20px; 
                        margin: 20px auto; 
                        max-width: 800px;
                        text-align: left;
                        overflow: auto;
                    }}
                    .btn {{ 
                        display: inline-block; 
                        background-color: #5c67de; 
                        color: white; 
                        padding: 10px 20px; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        margin-top: 20px; 
                    }}
                </style>
            </head>
            <body>
                <h1>Server Error</h1>
                <p>We encountered a problem processing your request.</p>
                <div class="error-box">
                    <strong>Error details:</strong><br>
                    {str(e)}
                    <hr>
                    <pre>{traceback.format_exc()}</pre>
                </div>
                <a href="/" class="btn">Go Back Home</a>
            </body>
            </html>
            """
            return [error_html.encode('utf-8')]

# Initialize the Appwrite connection
def init_appwrite():
    """Initialize and test Appwrite connection"""
    try:
        # Initialize appwrite_db to trigger configuration
        appwrite_db._ensure_initialized()
        print("Appwrite connection initialized successfully")
        return True
    except Exception as e:
        print(f"ERROR initializing Appwrite connection: {str(e)}")
        print("WARNING: Could not connect to Appwrite. Application will run in limited mode.")
        print("Some features requiring database access will not be available.")
        return False

# Test Appwrite connection
def test_appwrite_connection():
    """Test if Appwrite connection is working"""
    try:
        # Test by initializing the connection
        appwrite_db._ensure_initialized()
        return True
    except Exception as e:
        print(f"Failed to test Appwrite connection: {str(e)}")
        return False



# Utility function to ensure valid UUIDs
def safe_uuid(id_value):
    """Ensure a value is a valid UUID string or generate a new one"""
    if not id_value:
        return str(uuid.uuid4())
    
    try:
        # Test if it's a valid UUID
        uuid.UUID(str(id_value))
        return str(id_value)
    except (ValueError, TypeError, AttributeError) as e:
        print(f"WARNING: Invalid UUID '{id_value}' - generating new UUID")
        return str(uuid.uuid4())

# Safe query wrapper - DEPRECATED, use Appwrite directly
def query_table(table_name, query_type='select', fields='*', filters=None, data=None, limit=None):
    """
    DEPRECATED: This function has been replaced with direct Appwrite calls.
    Returns empty results to maintain compatibility.
    """
    from collections import namedtuple
    QueryResult = namedtuple('QueryResult', ['data', 'success', 'error'])
    
    print(f"WARNING: query_table() is deprecated. Use Appwrite directly for table '{table_name}'")
    return QueryResult(data=[], success=False, error="Function deprecated - use Appwrite directly")

# File upload helper function
def allowed_file(filename):
    """Check if a file has an allowed extension"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def business_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'business':
            flash('Access denied. Business account required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'customer':
            flash('Access denied. Customer account required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Function to generate a permanent business PIN
def generate_permanent_business_pin():
    """Generate a permanent 4-digit PIN for business identification"""
    import random
    import string
    
    # Generate a random 4-digit PIN (1000-9999)
    pin = f"{random.randint(1000, 9999):04d}"
    
    # Ensure the PIN doesn't start with 0 and avoid easily guessable patterns
    while (pin.startswith('0') or 
           pin == '1234' or pin == '0000' or pin == '9999' or 
           pin == '1111' or pin == '2222' or pin == '3333' or 
           pin == '4444' or pin == '5555' or pin == '6666' or 
           pin == '7777' or pin == '8888'):
        pin = f"{random.randint(1000, 9999):04d}"
    
    return pin

def check_pin_uniqueness(pin):
    """Check if the generated PIN is unique in the database"""
    try:
        from appwrite.query import Query
        businesses = appwrite_db.list_documents('businesses', [
            Query.equal('access_pin', pin),
            Query.limit(1)
        ])
        return len(businesses) == 0
    except Exception as e:
        print(f"Error checking PIN uniqueness: {e}")
        return True

def get_unique_business_pin():
    """Generate a unique business PIN that doesn't exist in the database"""
    max_attempts = 100
    for _ in range(max_attempts):
        pin = generate_permanent_business_pin()
        if check_pin_uniqueness(pin):
            return pin
    
    # Fallback: if we can't find a unique PIN after 100 attempts, 
    # use timestamp-based generation as last resort
    print("WARNING: Could not generate unique PIN, using timestamp fallback")
    return f"{int(datetime.now().timestamp()) % 10000:04d}"

# Function to generate QR code for business
def generate_business_qr_code(business_id, access_pin):
    if RENDER_DEPLOYMENT:
        return "static/images/placeholder_qr.png"
    
    try:
        # If QR code generation is not available, return placeholder
        try:
            import qrcode
            from PIL import Image
            QR_AVAILABLE = True
        except ImportError:
            print("QR code generation not available, using placeholder")
            return "static/images/placeholder_qr.png"
        
        # Make sure we have a valid PIN - if not, this is an error
        if not access_pin:
            print(f"ERROR: No access pin provided for QR code generation!")
            return "static/images/placeholder_qr.png"
        
        # Format: "business:PIN" - this is what the scanner expects
        qr_data = f"business:{access_pin}"
        print(f"Generating QR code with data: {qr_data}")
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        qr_folder = 'static/qr_codes'
        
        # Ensure the directory exists
        if not os.path.exists(qr_folder):
            os.makedirs(qr_folder)
            
        qr_filename = os.path.join(qr_folder, f"{business_id}.png")
        img.save(qr_filename)
        return qr_filename
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        # Return a default path that should exist
        return "static/images/placeholder_qr.png"

# Create Flask app with common configuration
def create_app(app_name='Khatape'):
    # Load environment variables
    load_dotenv()
    
    app = Flask(app_name)
    app.secret_key = os.getenv('SECRET_KEY', 'fc36290a52f89c1c92655b7d22b198e4')
    
    # Set session to be permanent (30 days)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
    
    # Apply our custom middleware
    app.wsgi_app = RequestLoggerMiddleware(app.wsgi_app)
    
    # Create folder structure
    upload_folder = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    os.makedirs(upload_folder, exist_ok=True)
    qr_folder = 'static/qr_codes'
    os.makedirs(qr_folder, exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Set up file upload configuration
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['QR_CODES_FOLDER'] = qr_folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    
    # Initialize Appwrite
    init_appwrite()
    
    return app

# Add template filter for datetime formatting
def format_datetime(value, format='%d %b %Y, %I:%M %p'):
    if isinstance(value, str):
        try:
            # Try to parse ISO format first
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            # If the datetime is already in IST (no timezone conversion needed)
            # We'll assume stored times are now in IST after our update
            return dt.strftime(format)
        except:
            return value
    elif hasattr(value, 'strftime'):
        return value.strftime(format)
    else:
        return str(value)
