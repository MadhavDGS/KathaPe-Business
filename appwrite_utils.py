"""
Appwrite Database Utilities - Replacement for PostgreSQL operations
"""
import json
import logging
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.exception import AppwriteException

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AppwriteDB:
    def __init__(self):
        self._initialized = False
        self.client = None
        self.databases = None
        self.database_id = None
        self.collections = None
        # Simple in-memory cache to reduce duplicate API calls
        self._cache = {}
        self._cache_ttl = 60  # Cache for 60 seconds
        
    def _ensure_initialized(self):
        """Initialize Appwrite config when first used"""
        if not self._initialized:
            # Initialize Appwrite client with optimization
            self.client = Client()
            self.client.set_endpoint(os.environ.get('APPWRITE_ENDPOINT', 'https://cloud.appwrite.io/v1'))
            self.client.set_project(os.environ.get('APPWRITE_PROJECT_ID', 'your_project_id'))
            self.client.set_key(os.environ.get('APPWRITE_API_KEY', 'your_api_key'))
            # Add headers for better performance
            self.client.add_header('Cache-Control', 'no-cache')
            self.client.add_header('Connection', 'keep-alive')

            # Initialize Databases service
            self.databases = Databases(self.client)

            # Database and collection configuration
            self.database_id = os.environ.get('APPWRITE_DATABASE_ID', 'kathape_business')
            self.collections = {
                'users': 'users',
                'businesses': 'businesses', 
                'customers': 'customers',
                'customer_credits': 'customer_credits',
                'transactions': 'transactions'
            }
            self._initialized = True
    
    def _get_cache_key(self, collection_name, document_id=None, query_hash=None):
        """Generate cache key"""
        if document_id:
            return f"{collection_name}:{document_id}"
        elif query_hash:
            return f"{collection_name}:query:{query_hash}"
        return None
    
    def _is_cache_valid(self, cache_key):
        """Check if cache entry is still valid"""
        if cache_key not in self._cache:
            return False
        import time
        return (time.time() - self._cache[cache_key]['timestamp']) < self._cache_ttl
    
    def _get_from_cache(self, cache_key):
        """Get data from cache"""
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]['data']
        return None
    
    def _set_cache(self, cache_key, data):
        """Set data in cache"""
        import time
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
        
    def create_document(self, collection_name, data, document_id=None):
        """Create a new document in collection"""
        try:
            self._ensure_initialized()
            if document_id is None:
                document_id = str(uuid.uuid4())
            # Add timestamps in IST
            from common_utils import get_ist_isoformat
            now = get_ist_isoformat()
            data['created_at'] = now
            data['updated_at'] = now
            result = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collections[collection_name],
                document_id=document_id,
                data=data
            )
            return result
        except AppwriteException as e:
            logger.error(f"Appwrite create error: {e}")
            return None

    def get_document(self, collection_name, document_id):
        """Get a single document by ID with caching"""
        try:
            self._ensure_initialized()
            
            # Check cache first
            cache_key = self._get_cache_key(collection_name, document_id)
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = self.databases.get_document(
                database_id=self.database_id,
                collection_id=self.collections[collection_name],
                document_id=document_id
            )
            
            # Cache the result
            if result:
                self._set_cache(cache_key, result)
            return result
        except AppwriteException as e:
            logger.error(f"Appwrite get error: {e}")
            return None

    def list_documents(self, collection_name, queries=None, limit=100):
        """List documents with optional queries"""
        try:
            self._ensure_initialized()
            if queries is None:
                queries = []
            queries.append(Query.limit(limit))
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.collections[collection_name],
                queries=queries
            )
            return result['documents']
        except AppwriteException as e:
            logger.error(f"Appwrite list error: {e}")
            return []

    def update_document(self, collection_name, document_id, data):
        """Update a document"""
        try:
            self._ensure_initialized()
            from common_utils import get_ist_isoformat
            data['updated_at'] = get_ist_isoformat()
            result = self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.collections[collection_name],
                document_id=document_id,
                data=data
            )
            return result
        except AppwriteException as e:
            logger.error(f"Appwrite update error: {e}")
            return None

    def delete_document(self, collection_name, document_id):
        """Delete a document"""
        try:
            self._ensure_initialized()
            self.databases.delete_document(
                database_id=self.database_id,
                collection_id=self.collections[collection_name],
                document_id=document_id
            )
            return True
        except AppwriteException as e:
            logger.error(f"Appwrite delete error: {e}")
            return False

    def query_documents(self, collection_name, filters=None, limit=100):
        """Query documents with filters"""
        try:
            self._ensure_initialized()
            queries = []
            if filters:
                for key, value in filters.items():
                    if isinstance(value, dict):
                        for op, val in value.items():
                            if op == '$gt':
                                queries.append(Query.greater_than(key, val))
                            elif op == '$gte':
                                queries.append(Query.greater_than_equal(key, val))
                            elif op == '$lt':
                                queries.append(Query.less_than(key, val))
                            elif op == '$lte':
                                queries.append(Query.less_than_equal(key, val))
                            elif op == '$ne':
                                queries.append(Query.not_equal(key, val))
                    else:
                        queries.append(Query.equal(key, value))
            queries.append(Query.limit(limit))
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.collections[collection_name],
                queries=queries
            )
            return result['documents']
        except AppwriteException as e:
            logger.error(f"Appwrite query error: {e}")
            return []

# Global database instance
db = AppwriteDB()

# Helper functions to replace PostgreSQL operations

def get_user_by_phone(phone_number):
    """Get user by phone number"""
    try:
        users = db.query_documents('users', {'phone_number': phone_number}, limit=1)
        return users[0] if users else None
    except Exception as e:
        logger.error(f"Error getting user by phone: {e}")
        return None

def get_business_by_user_id(user_id):
    """Get business by user ID"""
    try:
        businesses = db.query_documents('businesses', {'user_id': user_id}, limit=1)
        return businesses[0] if businesses else None
    except Exception as e:
        logger.error(f"Error getting business by user ID: {e}")
        return None

def create_user(user_data):
    """Create a new user"""
    try:
        return db.create_document('users', user_data)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None

def create_business(business_data):
    """Create a new business"""
    try:
        return db.create_document('businesses', business_data)
    except Exception as e:
        logger.error(f"Error creating business: {e}")
        return None

def create_customer(customer_data):
    """Create a new customer"""
    try:
        return db.create_document('customers', customer_data)
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        return None

def get_customer_by_phone(phone_number):
    """Get customer by phone number"""
    try:
        customers = db.query_documents('customers', {'phone_number': phone_number}, limit=1)
        return customers[0] if customers else None
    except Exception as e:
        logger.error(f"Error getting customer by phone: {e}")
        return None

def get_customer_credit_by_business_and_customer(business_id, customer_id):
    """Get customer credit relationship"""
    try:
        credits = db.query_documents('customer_credits', {
            'business_id': business_id,
            'customer_id': customer_id
        }, limit=1)
        return credits[0] if credits else None
    except Exception as e:
        logger.error(f"Error getting customer credit: {e}")
        return None

def create_customer_credit(credit_data):
    """Create a new customer credit record"""
    try:
        return db.create_document('customer_credits', credit_data)
    except Exception as e:
        logger.error(f"Error creating customer credit: {e}")
        return None

def update_customer_credit(credit_id, update_data):
    """Update customer credit record"""
    try:
        return db.update_document('customer_credits', credit_id, update_data)
    except Exception as e:
        logger.error(f"Error updating customer credit: {e}")
        return None

def create_transaction(transaction_data):
    """Create a new transaction"""
    try:
        return db.create_document('transactions', transaction_data)
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        return None

def get_transactions_by_business_and_customer(business_id, customer_id):
    """Get transactions for a business-customer relationship"""
    try:
        return db.query_documents('transactions', {
            'business_id': business_id,
            'customer_id': customer_id
        })
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        return []

def get_customers_by_business(business_id):
    """Get all customers for a business"""
    try:
        return db.query_documents('customer_credits', {'business_id': business_id})
    except Exception as e:
        logger.error(f"Error getting business customers: {e}")
        return []

def get_customer_by_id(customer_id):
    """Get customer by ID"""
    try:
        return db.get_document('customers', customer_id)
    except Exception as e:
        logger.error(f"Error getting customer by ID: {e}")
        return None

def get_transaction_by_id(transaction_id):
    """Get a single transaction by ID"""
    try:
        return db.get_document('transactions', transaction_id)
    except Exception as e:
        logger.error(f"Error getting transaction by ID: {e}")
        return None
