
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases

# Load environment variables
load_dotenv()

class AppwriteConfig:
    def __init__(self):
        # Initialize Appwrite client
        self.client = Client()
        self.client.set_endpoint(os.environ.get('APPWRITE_ENDPOINT', 'https://cloud.appwrite.io/v1'))
        self.client.set_project(os.environ.get('APPWRITE_PROJECT_ID', 'your_project_id'))
        self.client.set_key(os.environ.get('APPWRITE_API_KEY', 'your_api_key'))

        # Initialize Databases service
        self.databases = Databases(self.client)
        self.database_id = os.environ.get('APPWRITE_DATABASE_ID', 'kathape_business')
        
        # Collection mapping
        self.collections = {
            'users': 'users',
            'businesses': 'businesses', 
            'customers': 'customers',
            'customer_credits': 'customer_credits',
            'transactions': 'transactions'
        }

    def get_databases(self):
        return self.databases

# Global instances for compatibility
appwrite_db = AppwriteConfig()

def get_current_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def safe_uuid_appwrite(value):
    """Generate a safe UUID for Appwrite"""
    if value is None:
        return str(uuid.uuid4())
    return str(value)
