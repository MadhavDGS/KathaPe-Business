"""
Appwrite Configuration Module
Handles Appwrite client initialization and configuration
"""

import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases

class AppwriteConfig:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get configuration from environment variables
        self.endpoint = os.getenv('APPWRITE_ENDPOINT')
        self.project_id = os.getenv('APPWRITE_PROJECT_ID')
        self.api_key = os.getenv('APPWRITE_API_KEY')
        self.database_id = os.getenv('APPWRITE_DATABASE_ID', 'kathape_business_db')
        
        # Collection IDs
        self.collections = {
            'users': os.getenv('APPWRITE_COLLECTION_USERS', 'users'),
            'businesses': os.getenv('APPWRITE_COLLECTION_BUSINESSES', 'businesses'),
            'customers': os.getenv('APPWRITE_COLLECTION_CUSTOMERS', 'customers'),
            'customer_credits': os.getenv('APPWRITE_COLLECTION_CUSTOMER_CREDITS', 'customer_credits'),
            'transactions': os.getenv('APPWRITE_COLLECTION_TRANSACTIONS', 'transactions')
        }
        
        # Validate required configurations
        if not all([self.endpoint, self.project_id, self.api_key]):
            raise ValueError("Missing required Appwrite configuration. Please check your .env file.")
        
        # Initialize client
        self._client = None
        self._databases = None
    
    def get_client(self):
        """Get initialized Appwrite client"""
        if self._client is None:
            self._client = Client()
            self._client.set_endpoint(self.endpoint)
            self._client.set_project(self.project_id)
            self._client.set_key(self.api_key)
        return self._client
    
    def get_databases(self):
        """Get initialized Databases service"""
        if self._databases is None:
            client = self.get_client()
            self._databases = Databases(client)
        return self._databases
