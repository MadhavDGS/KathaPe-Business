"""
Appwrite Database Utilities - Replacement for PostgreSQL operations
"""
<<<<<<< HEAD
import json
import logging
from datetime import datetime
from appwrite.query import Query
from appwrite.exception import AppwriteException
=======
from appwrite_config import appwrite_db, get_current_timestamp, safe_uuid_appwrite
from appwrite.query import Query
from appwrite.exception import AppwriteException
import json
import logging
>>>>>>> 64f183b76de57e07d1178b54e0a01fc6ea9fbb6a

logger = logging.getLogger(__name__)

class AppwriteDB:
    def __init__(self):
<<<<<<< HEAD
        self.config = None
        self.databases = None
        self._initialized = False
        
    def _ensure_initialized(self):
        """Initialize Appwrite config when first used"""
        if not self._initialized:
            from appwrite_config import AppwriteConfig
            self.config = AppwriteConfig()
            self.databases = self.config.get_databases()
            self._initialized = True
=======
        self.db = appwrite_db
>>>>>>> 64f183b76de57e07d1178b54e0a01fc6ea9fbb6a
        
    def create_document(self, collection_name, data, document_id=None):
        """Create a new document in collection"""
        try:
<<<<<<< HEAD
            self._ensure_initialized()
            
            if not self.databases:
                logger.error("Appwrite not available")
                return None
            
            # Add timestamps
            if 'created_at' not in data:
                data['created_at'] = datetime.now().isoformat()
            if 'updated_at' not in data:
                data['updated_at'] = datetime.now().isoformat()
            
            result = self.databases.create_document(
                database_id=self.config.database_id,
                collection_id=self.config.collections[collection_name],
                document_id=document_id or 'unique()',
                data=data
            )
            return result
        except Exception as e:
=======
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
>>>>>>> 64f183b76de57e07d1178b54e0a01fc6ea9fbb6a
            logger.error(f"Appwrite create error: {e}")
            return None

    def get_document(self, collection_name, document_id):
        """Get a single document by ID"""
        try:
<<<<<<< HEAD
            self._ensure_initialized()
            
            if not self.databases:
                return None
                
            result = self.databases.get_document(
                database_id=self.config.database_id,
                collection_id=self.config.collections[collection_name],
                document_id=document_id
            )
            return result
        except Exception as e:
            logger.error(f"Appwrite get error: {e}")
            return None

    def list_documents(self, collection_name, queries=None):
        """List documents with optional queries"""
        try:
            self._ensure_initialized()
            
            if not self.databases:
                return []
            
            result = self.databases.list_documents(
                database_id=self.config.database_id,
                collection_id=self.config.collections[collection_name],
                queries=queries
            )
            return result['documents']
        except Exception as e:
=======
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
>>>>>>> 64f183b76de57e07d1178b54e0a01fc6ea9fbb6a
            logger.error(f"Appwrite list error: {e}")
            return []

    def update_document(self, collection_name, document_id, data):
        """Update a document"""
        try:
<<<<<<< HEAD
            self._ensure_initialized()
            
            if not self.databases:
                return None
            
            data['updated_at'] = datetime.now().isoformat()
            
            result = self.databases.update_document(
                database_id=self.config.database_id,
                collection_id=self.config.collections[collection_name],
=======
            data['updated_at'] = get_current_timestamp()
            
            result = self.db.databases.update_document(
                database_id=self.db.database_id,
                collection_id=self.db.collections[collection_name],
>>>>>>> 64f183b76de57e07d1178b54e0a01fc6ea9fbb6a
                document_id=document_id,
                data=data
            )
            return result
<<<<<<< HEAD
        except Exception as e:
=======
        except AppwriteException as e:
>>>>>>> 64f183b76de57e07d1178b54e0a01fc6ea9fbb6a
            logger.error(f"Appwrite update error: {e}")
            return None

    def delete_document(self, collection_name, document_id):
        """Delete a document"""
        try:
<<<<<<< HEAD
            self._ensure_initialized()
            
            if not self.databases:
                return False
                
            self.databases.delete_document(
                database_id=self.config.database_id,
                collection_id=self.config.collections[collection_name],
                document_id=document_id
            )
            return True
        except Exception as e:
=======
            self.db.databases.delete_document(
                database_id=self.db.database_id,
                collection_id=self.db.collections[collection_name],
                document_id=document_id
            )
            return True
        except AppwriteException as e:
>>>>>>> 64f183b76de57e07d1178b54e0a01fc6ea9fbb6a
            logger.error(f"Appwrite delete error: {e}")
            return False

    def query_documents(self, collection_name, filters=None, limit=100):
        """Query documents with filters"""
        try:
<<<<<<< HEAD
            self._ensure_initialized()
            
            if not self.databases:
                return []
            
            # Simple approach: get all documents and filter manually for now
            result = self.databases.list_documents(
                database_id=self.config.database_id,
                collection_id=self.config.collections[collection_name],
                queries=None
            )
            
            documents = result['documents']
            
            # Apply filters manually if any
            if filters:
                filtered_docs = []
                for doc in documents:
                    match = True
                    for key, value in filters.items():
                        if key not in doc or doc[key] != value:
                            match = False
                            break
                    if match:
                        filtered_docs.append(doc)
                        if len(filtered_docs) >= limit:
                            break
                return filtered_docs
            
            return documents[:limit]
            
        except Exception as e:
=======
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
>>>>>>> 64f183b76de57e07d1178b54e0a01fc6ea9fbb6a
            logger.error(f"Appwrite query error: {e}")
            return []

# Global database instance
db = AppwriteDB()

# Helper functions to replace PostgreSQL operations

def get_user_by_phone(phone_number):
    """Get user by phone number"""
<<<<<<< HEAD
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
=======
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
>>>>>>> 64f183b76de57e07d1178b54e0a01fc6ea9fbb6a
