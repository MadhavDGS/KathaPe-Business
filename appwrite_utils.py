"""
Appwrite Database Utilities - Replacement for PostgreSQL operations
"""
from appwrite_config import appwrite_db, get_current_timestamp, safe_uuid_appwrite
from appwrite.query import Query
from appwrite.exception import AppwriteException
import json
import logging

logger = logging.getLogger(__name__)

class AppwriteDB:
    def __init__(self):
        self.db = appwrite_db
        
    def create_document(self, collection_name, data, document_id=None):
        """Create a new document in collection"""
        try:
            if document_id is None:
                document_id = safe_uuid_appwrite(None)
            
            # Add timestamps
            data['created_at'] = get_current_timestamp()
            data['updated_at'] = get_current_timestamp()
            
            result = self.db.databases.create_document(
                database_id=self.db.database_id,
                collection_id=self.db.collections[collection_name],
                document_id=document_id,
                data=data
            )
            return result
        except AppwriteException as e:
            logger.error(f"Appwrite create error: {e}")
            return None

    def get_document(self, collection_name, document_id):
        """Get a single document by ID"""
        try:
            result = self.db.databases.get_document(
                database_id=self.db.database_id,
                collection_id=self.db.collections[collection_name],
                document_id=document_id
            )
            return result
        except AppwriteException as e:
            logger.error(f"Appwrite get error: {e}")
            return None

    def list_documents(self, collection_name, queries=None, limit=100):
        """List documents with optional queries"""
        try:
            if queries is None:
                queries = []
            
            queries.append(Query.limit(limit))
            
            result = self.db.databases.list_documents(
                database_id=self.db.database_id,
                collection_id=self.db.collections[collection_name],
                queries=queries
            )
            return result['documents']
        except AppwriteException as e:
            logger.error(f"Appwrite list error: {e}")
            return []

    def update_document(self, collection_name, document_id, data):
        """Update a document"""
        try:
            data['updated_at'] = get_current_timestamp()
            
            result = self.db.databases.update_document(
                database_id=self.db.database_id,
                collection_id=self.db.collections[collection_name],
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
            self.db.databases.delete_document(
                database_id=self.db.database_id,
                collection_id=self.db.collections[collection_name],
                document_id=document_id
            )
            return True
        except AppwriteException as e:
            logger.error(f"Appwrite delete error: {e}")
            return False

    def query_documents(self, collection_name, filters=None, limit=100):
        """Query documents with filters"""
        try:
            queries = []
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, dict):
                        # Handle operators like {'$gt': 0}
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
            
            result = self.db.databases.list_documents(
                database_id=self.db.database_id,
                collection_id=self.db.collections[collection_name],
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
    users = db.query_documents('users', {'phone_number': phone_number}, limit=1)
    return users[0] if users else None

def get_business_by_user_id(user_id):
    """Get business by user ID"""
    businesses = db.query_documents('businesses', {'user_id': user_id}, limit=1)
    return businesses[0] if businesses else None

def get_customers_with_balance(business_id):
    """Get customers with positive balance"""
    return db.query_documents('customers', {
        'business_id': business_id,
        'balance': {'$gt': 0}
    })

def get_customer_transactions(business_id, customer_id, limit=10):
    """Get customer transactions"""
    return db.query_documents('transactions', {
        'business_id': business_id,
        'customer_id': customer_id
    }, limit=limit)

def create_transaction(business_id, customer_id, amount, transaction_type, description, receipt_image_url=None):
    """Create a new transaction"""
    transaction_data = {
        'business_id': business_id,
        'customer_id': customer_id,
        'amount': float(amount),
        'transaction_type': transaction_type,
        'description': description,
    }
    
    if receipt_image_url:
        transaction_data['receipt_image_url'] = receipt_image_url
    
    return db.create_document('transactions', transaction_data)

def update_customer_balance(customer_id, new_balance):
    """Update customer balance"""
    return db.update_document('customers', customer_id, {'balance': float(new_balance)})

def get_business_customers(business_id, limit=50):
    """Get all customers for a business"""
    return db.query_documents('customers', {'business_id': business_id}, limit=limit)

def create_customer(business_id, name, phone, email=None, address=None):
    """Create a new customer"""
    customer_data = {
        'business_id': business_id,
        'name': name,
        'phone': phone,
        'balance': 0.0
    }
    
    if email:
        customer_data['email'] = email
    if address:
        customer_data['address'] = address
    
    return db.create_document('customers', customer_data)
