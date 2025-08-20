"""
Database Migration Helper for App.py
This file contains replacement functions for all database operations
"""

from appwrite_utils import AppwriteDB
from datetime import datetime
from appwrite.query import Query

# Initialize Appwrite DB
appwrite_db = AppwriteDB()

def execute_query_replacement(query, params=None, fetch_one=False, commit=True):
    """
    Replacement function for execute_query that translates SQL to Appwrite operations
    This function analyzes the SQL query and converts it to appropriate Appwrite calls
    """
    
    # Normalize the query for easier parsing
    query_lower = query.lower().strip()
    
    try:
        # Handle SELECT queries
        if query_lower.startswith('select'):
            return handle_select_query(query, params, fetch_one)
        
        # Handle INSERT queries
        elif query_lower.startswith('insert'):
            return handle_insert_query(query, params)
        
        # Handle UPDATE queries
        elif query_lower.startswith('update'):
            return handle_update_query(query, params)
        
        # Handle DELETE queries
        elif query_lower.startswith('delete'):
            return handle_delete_query(query, params)
        
        else:
            print(f"Unsupported query type: {query}")
            return None
            
    except Exception as e:
        print(f"Error executing query replacement: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        return None

def handle_select_query(query, params=None, fetch_one=False):
    """Handle SELECT queries"""
    query_lower = query.lower()
    
    # Parse table name
    if 'from users' in query_lower:
        collection = 'users'
    elif 'from businesses' in query_lower:
        collection = 'businesses'
    elif 'from customers' in query_lower:
        collection = 'customers'
    elif 'from customer_credits' in query_lower:
        collection = 'customer_credits'
    elif 'from transactions' in query_lower:
        collection = 'transactions'
    else:
        print(f"Unknown table in query: {query}")
        return None
    
    # Build query conditions
    queries = []
    
    if params and 'where' in query_lower:
        # Parse WHERE conditions based on common patterns
        if 'phone_number = ' in query_lower:
            queries.append(Query.equal('phone_number', params[0]))
        elif 'id = ' in query_lower:
            queries.append(Query.equal('$id', params[0]))
        elif 'business_id = ' in query_lower and 'customer_id = ' in query_lower:
            queries.append(Query.equal('business_id', params[0]))
            queries.append(Query.equal('customer_id', params[1]))
        elif 'business_id = ' in query_lower:
            queries.append(Query.equal('business_id', params[0]))
        elif 'customer_id = ' in query_lower:
            queries.append(Query.equal('customer_id', params[0]))
        elif 'user_id = ' in query_lower:
            queries.append(Query.equal('user_id', params[0]))
        elif 'access_pin = ' in query_lower:
            queries.append(Query.equal('access_pin', params[0]))
    
    # Add ordering if present
    if 'order by' in query_lower:
        if 'created_at desc' in query_lower:
            queries.append(Query.order_desc('created_at'))
        elif 'created_at' in query_lower:
            queries.append(Query.order_asc('created_at'))
    
    # Add limit if present
    if 'limit' in query_lower:
        if 'limit 1' in query_lower:
            queries.append(Query.limit(1))
        elif fetch_one:
            queries.append(Query.limit(1))
    
    try:
        # Execute query
        if fetch_one or 'limit 1' in query_lower:
            result = appwrite_db.databases.list_documents(
                database_id=appwrite_db.config.database_id,
                collection_id=appwrite_db.config.collections[collection],
                queries=queries
            )
            if result['documents']:
                # Convert Appwrite document to dict-like object for compatibility
                doc = result['documents'][0]
                return dict(doc)
            return None
        else:
            result = appwrite_db.databases.list_documents(
                database_id=appwrite_db.config.database_id,
                collection_id=appwrite_db.config.collections[collection],
                queries=queries
            )
            # Convert all documents to dict-like objects
            return [dict(doc) for doc in result['documents']]
    
    except Exception as e:
        print(f"Error in SELECT query: {e}")
        return None

def handle_insert_query(query, params=None):
    """Handle INSERT queries"""
    query_lower = query.lower()
    
    # Parse table name
    if 'into users' in query_lower:
        collection = 'users'
    elif 'into businesses' in query_lower:
        collection = 'businesses'
    elif 'into customers' in query_lower:
        collection = 'customers'
    elif 'into customer_credits' in query_lower:
        collection = 'customer_credits'
    elif 'into transactions' in query_lower:
        collection = 'transactions'
    else:
        print(f"Unknown table in INSERT query: {query}")
        return None
    
    # Create document data based on common INSERT patterns
    document_data = {}
    
    # Parse INSERT patterns for each table
    if collection == 'users' and params:
        if len(params) >= 6:  # id, name, phone, user_type, password, created_at
            document_data = {
                'name': params[1],
                'phone_number': params[2],
                'user_type': params[3],
                'password': params[4],
                'created_at': params[5] if len(params) > 5 else datetime.now().isoformat(),
                'is_active': True
            }
            document_id = params[0]
    
    elif collection == 'businesses' and params:
        if len(params) >= 6:  # id, user_id, name, description, access_pin, created_at
            document_data = {
                'user_id': params[1],
                'name': params[2],
                'description': params[3],
                'access_pin': params[4],
                'created_at': params[5] if len(params) > 5 else datetime.now().isoformat(),
                'is_active': True
            }
            document_id = params[0]
    
    elif collection == 'customers' and params:
        if len(params) >= 4:  # id, name, phone, created_at
            document_data = {
                'name': params[1],
                'phone_number': params[2],
                'created_at': params[3] if len(params) > 3 else datetime.now().isoformat(),
                'is_active': True
            }
            document_id = params[0]
    
    elif collection == 'customer_credits' and params:
        if len(params) >= 4:  # id, business_id, customer_id, current_balance, created_at
            document_data = {
                'business_id': params[1],
                'customer_id': params[2],
                'current_balance': params[3] if len(params) > 3 else 0.0,
                'credit_limit': 0.0,
                'created_at': datetime.now().isoformat(),
                'is_active': True
            }
            document_id = params[0]
    
    elif collection == 'transactions' and params:
        # More complex parsing needed for transactions
        document_data = parse_transaction_insert(query, params)
        document_id = params[0] if params else None
    
    try:
        # Create document in Appwrite
        result = appwrite_db.databases.create_document(
            database_id=appwrite_db.config.database_id,
            collection_id=appwrite_db.config.collections[collection],
            document_id=document_id or 'unique()',
            data=document_data
        )
        return dict(result)
    
    except Exception as e:
        print(f"Error in INSERT query: {e}")
        return None

def handle_update_query(query, params=None):
    """Handle UPDATE queries"""
    query_lower = query.lower()
    
    # Parse table name
    if 'update users' in query_lower:
        collection = 'users'
    elif 'update businesses' in query_lower:
        collection = 'businesses'
    elif 'update customers' in query_lower:
        collection = 'customers'
    elif 'update customer_credits' in query_lower:
        collection = 'customer_credits'
    elif 'update transactions' in query_lower:
        collection = 'transactions'
    else:
        print(f"Unknown table in UPDATE query: {query}")
        return None
    
    # Parse SET and WHERE clauses
    # This is a simplified implementation - extend as needed
    try:
        # For now, implement specific UPDATE patterns as encountered
        print(f"UPDATE query not fully implemented yet: {query}")
        return None
    except Exception as e:
        print(f"Error in UPDATE query: {e}")
        return None

def handle_delete_query(query, params=None):
    """Handle DELETE queries"""
    # Implement as needed
    print(f"DELETE query not implemented yet: {query}")
    return None

def parse_transaction_insert(query, params):
    """Parse transaction INSERT query parameters"""
    # This needs to be customized based on the actual INSERT query structure
    if not params or len(params) < 6:
        return {}
    
    return {
        'business_id': params[1],
        'customer_id': params[2],
        'amount': float(params[3]),
        'transaction_type': params[4],
        'notes': params[5] if len(params) > 5 else '',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

# Function to replace execute_query calls in app.py
def migrate_execute_query_calls():
    """
    This function can be used to replace execute_query calls with the new implementation
    """
    global execute_query
    execute_query = execute_query_replacement
    print("Database migration helper loaded. execute_query calls will now use Appwrite.")
