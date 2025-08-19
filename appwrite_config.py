"""
Appwrite Database Configuration and Collections Setup
"""
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.id import ID
import os
from datetime import datetime

class AppwriteConfig:
    def __init__(self):
        # Initialize Appwrite client
        self.client = Client()
        self.client.set_endpoint(os.environ.get('APPWRITE_ENDPOINT', 'https://cloud.appwrite.io/v1'))
        self.client.set_project(os.environ.get('APPWRITE_PROJECT_ID'))
        self.client.set_key(os.environ.get('APPWRITE_API_KEY'))
        
        self.databases = Databases(self.client)
        self.users = Users(self.client)
        
        # Database and Collection IDs
        self.database_id = os.environ.get('APPWRITE_DATABASE_ID', 'kathape_business')
        
        # Collection IDs (you'll need to create these in Appwrite console)
        self.collections = {
            'users': 'users',
            'businesses': 'businesses', 
            'customers': 'customers',
            'transactions': 'transactions',
            'customer_credits': 'customer_credits',
            'reminders': 'reminders'
        }

# Global Appwrite instance
appwrite_db = AppwriteConfig()

def get_current_timestamp():
    """Get current timestamp in ISO format for Appwrite"""
    return datetime.utcnow().isoformat() + 'Z'

def safe_uuid_appwrite(value):
    """Generate safe UUID for Appwrite documents"""
    if not value or value == 'None':
        return ID.unique()
    return str(value)

# Collection schema definitions for reference
COLLECTION_SCHEMAS = {
    'users': {
        'name': 'string',
        'phone_number': 'string',
        'email': 'string', 
        'user_type': 'string',  # 'business' or 'customer'
        'password': 'string',
        'profile_photo_url': 'string',
        'is_active': 'boolean',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    },
    'businesses': {
        'user_id': 'string',
        'name': 'string',
        'description': 'string',
        'business_type': 'string',
        'address': 'string',
        'city': 'string',
        'state': 'string',
        'pincode': 'string',
        'access_pin': 'string',
        'qr_code_data': 'string',
        'is_active': 'boolean',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    },
    'customers': {
        'business_id': 'string',
        'name': 'string',
        'phone': 'string',
        'email': 'string',
        'address': 'string',
        'balance': 'float',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    },
    'transactions': {
        'business_id': 'string',
        'customer_id': 'string',
        'amount': 'float',
        'transaction_type': 'string',  # 'credit' or 'debit'
        'description': 'string',
        'receipt_image_url': 'string',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    },
    'customer_credits': {
        'business_id': 'string',
        'customer_id': 'string',
        'amount': 'float',
        'description': 'string',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    },
    'reminders': {
        'business_id': 'string',
        'customer_id': 'string',
        'amount': 'float',
        'message': 'string',
        'status': 'string',  # 'sent', 'pending', 'failed'
        'sent_at': 'datetime',
        'created_at': 'datetime'
    }
}
