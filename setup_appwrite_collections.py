#!/usr/bin/env python3
"""
Appwrite Collections Setup Script
This script creates the necessary collections in Appwrite to replace PostgreSQL tables
Based on the database_schema.sql file
"""

import os
import sys
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.exception import AppwriteException
from appwrite_config import AppwriteConfig

def setup_collections():
    """Create all necessary collections in Appwrite"""
    
    # Initialize Appwrite client
    config = AppwriteConfig()
    databases = config.get_databases()
    
    try:
        # Create database if it doesn't exist
        try:
            result = databases.get(config.database_id)
            print(f"Database '{config.database_id}' already exists")
        except AppwriteException as e:
            if e.code == 404:
                print(f"Creating database '{config.database_id}'...")
                databases.create(
                    database_id=config.database_id,
                    name="KathaPe Business Database"
                )
                print("Database created successfully!")
            else:
                raise e
        
        # Collection configurations
        collections = [
            {
                'id': config.collections['users'],
                'name': 'Users',
                'attributes': [
                    {'key': 'name', 'type': 'string', 'size': 255, 'required': True},
                    {'key': 'phone_number', 'type': 'string', 'size': 20, 'required': True},
                    {'key': 'email', 'type': 'string', 'size': 255, 'required': False},
                    {'key': 'user_type', 'type': 'enum', 'elements': ['business', 'customer'], 'required': True},
                    {'key': 'password', 'type': 'string', 'size': 255, 'required': True},
                    {'key': 'profile_photo_url', 'type': 'string', 'size': 500, 'required': False},
                    {'key': 'is_active', 'type': 'boolean', 'required': False, 'default': True},
                    {'key': 'created_at', 'type': 'datetime', 'required': False},
                    {'key': 'updated_at', 'type': 'datetime', 'required': False}
                ],
                'indexes': [
                    {'key': 'phone_number_index', 'type': 'unique', 'attributes': ['phone_number']},
                    {'key': 'user_type_index', 'type': 'key', 'attributes': ['user_type']},
                    {'key': 'created_at_index', 'type': 'key', 'attributes': ['created_at']}
                ]
            },
            {
                'id': config.collections['businesses'],
                'name': 'Businesses',
                'attributes': [
                    {'key': 'user_id', 'type': 'string', 'size': 36, 'required': True},
                    {'key': 'name', 'type': 'string', 'size': 255, 'required': True},
                    {'key': 'description', 'type': 'string', 'size': 1000, 'required': False},
                    {'key': 'business_type', 'type': 'string', 'size': 100, 'required': False},
                    {'key': 'address', 'type': 'string', 'size': 500, 'required': False},
                    {'key': 'city', 'type': 'string', 'size': 100, 'required': False},
                    {'key': 'state', 'type': 'string', 'size': 100, 'required': False},
                    {'key': 'pincode', 'type': 'string', 'size': 10, 'required': False},
                    {'key': 'access_pin', 'type': 'string', 'size': 10, 'required': True},
                    {'key': 'qr_code_data', 'type': 'string', 'size': 1000, 'required': False},
                    {'key': 'is_active', 'type': 'boolean', 'required': False, 'default': True},
                    {'key': 'created_at', 'type': 'datetime', 'required': False},
                    {'key': 'updated_at', 'type': 'datetime', 'required': False}
                ],
                'indexes': [
                    {'key': 'user_id_index', 'type': 'key', 'attributes': ['user_id']},
                    {'key': 'access_pin_index', 'type': 'key', 'attributes': ['access_pin']},
                    {'key': 'created_at_index', 'type': 'key', 'attributes': ['created_at']}
                ]
            },
            {
                'id': config.collections['customers'],
                'name': 'Customers',
                'attributes': [
                    {'key': 'name', 'type': 'string', 'size': 255, 'required': True},
                    {'key': 'phone_number', 'type': 'string', 'size': 20, 'required': True},
                    {'key': 'email', 'type': 'string', 'size': 255, 'required': False},
                    {'key': 'address', 'type': 'string', 'size': 500, 'required': False},
                    {'key': 'city', 'type': 'string', 'size': 100, 'required': False},
                    {'key': 'state', 'type': 'string', 'size': 100, 'required': False},
                    {'key': 'pincode', 'type': 'string', 'size': 10, 'required': False},
                    {'key': 'profile_photo_url', 'type': 'string', 'size': 500, 'required': False},
                    {'key': 'is_active', 'type': 'boolean', 'required': False, 'default': True},
                    {'key': 'created_at', 'type': 'datetime', 'required': False},
                    {'key': 'updated_at', 'type': 'datetime', 'required': False}
                ],
                'indexes': [
                    {'key': 'phone_number_index', 'type': 'unique', 'attributes': ['phone_number']},
                    {'key': 'created_at_index', 'type': 'key', 'attributes': ['created_at']}
                ]
            },
            {
                'id': config.collections['customer_credits'],
                'name': 'Customer Credits',
                'attributes': [
                    {'key': 'business_id', 'type': 'string', 'size': 36, 'required': True},
                    {'key': 'customer_id', 'type': 'string', 'size': 36, 'required': True},
                    {'key': 'current_balance', 'type': 'double', 'required': False, 'default': 0.0},
                    {'key': 'credit_limit', 'type': 'double', 'required': False, 'default': 0.0},
                    {'key': 'is_active', 'type': 'boolean', 'required': False, 'default': True},
                    {'key': 'created_at', 'type': 'datetime', 'required': False},
                    {'key': 'updated_at', 'type': 'datetime', 'required': False}
                ],
                'indexes': [
                    {'key': 'business_id_index', 'type': 'key', 'attributes': ['business_id']},
                    {'key': 'customer_id_index', 'type': 'key', 'attributes': ['customer_id']},
                    {'key': 'business_customer_index', 'type': 'unique', 'attributes': ['business_id', 'customer_id']},
                    {'key': 'balance_index', 'type': 'key', 'attributes': ['current_balance']},
                    {'key': 'created_at_index', 'type': 'key', 'attributes': ['created_at']}
                ]
            },
            {
                'id': config.collections['transactions'],
                'name': 'Transactions',
                'attributes': [
                    {'key': 'business_id', 'type': 'string', 'size': 36, 'required': True},
                    {'key': 'customer_id', 'type': 'string', 'size': 36, 'required': True},
                    {'key': 'amount', 'type': 'double', 'required': True},
                    {'key': 'transaction_type', 'type': 'enum', 'elements': ['credit', 'payment'], 'required': True},
                    {'key': 'notes', 'type': 'string', 'size': 1000, 'required': False},
                    {'key': 'media_url', 'type': 'string', 'size': 500, 'required': False},
                    {'key': 'receipt_image_url', 'type': 'string', 'size': 500, 'required': False},
                    {'key': 'transaction_reference', 'type': 'string', 'size': 100, 'required': False},
                    {'key': 'payment_method', 'type': 'string', 'size': 50, 'required': False},
                    {'key': 'created_by', 'type': 'string', 'size': 36, 'required': False},
                    {'key': 'created_at', 'type': 'datetime', 'required': False},
                    {'key': 'updated_at', 'type': 'datetime', 'required': False}
                ],
                'indexes': [
                    {'key': 'business_id_index', 'type': 'key', 'attributes': ['business_id']},
                    {'key': 'customer_id_index', 'type': 'key', 'attributes': ['customer_id']},
                    {'key': 'transaction_type_index', 'type': 'key', 'attributes': ['transaction_type']},
                    {'key': 'business_customer_index', 'type': 'key', 'attributes': ['business_id', 'customer_id']},
                    {'key': 'created_at_index', 'type': 'key', 'attributes': ['created_at']},
                    {'key': 'amount_index', 'type': 'key', 'attributes': ['amount']}
                ]
            }
        ]
        
        # Create each collection
        for collection_config in collections:
            try:
                # Check if collection exists
                try:
                    existing = databases.get_collection(config.database_id, collection_config['id'])
                    print(f"Collection '{collection_config['name']}' already exists")
                    continue
                except AppwriteException as e:
                    if e.code != 404:
                        raise e
                
                # Create collection
                print(f"Creating collection '{collection_config['name']}'...")
                collection = databases.create_collection(
                    database_id=config.database_id,
                    collection_id=collection_config['id'],
                    name=collection_config['name'],
                    permissions=[
                        Permission.read(Role.any()),
                        Permission.create(Role.any()),
                        Permission.update(Role.any()),
                        Permission.delete(Role.any())
                    ]
                )
                
                # Create attributes
                for attr in collection_config['attributes']:
                    print(f"  Creating attribute '{attr['key']}'...")
                    
                    if attr['type'] == 'string':
                        databases.create_string_attribute(
                            database_id=config.database_id,
                            collection_id=collection_config['id'],
                            key=attr['key'],
                            size=attr['size'],
                            required=attr['required'],
                            default=attr.get('default', None),
                            array=False
                        )
                    elif attr['type'] == 'boolean':
                        databases.create_boolean_attribute(
                            database_id=config.database_id,
                            collection_id=collection_config['id'],
                            key=attr['key'],
                            required=attr['required'],
                            default=attr.get('default', None),
                            array=False
                        )
                    elif attr['type'] == 'double':
                        databases.create_float_attribute(
                            database_id=config.database_id,
                            collection_id=collection_config['id'],
                            key=attr['key'],
                            required=attr['required'],
                            min=None,
                            max=None,
                            default=attr.get('default', None),
                            array=False
                        )
                    elif attr['type'] == 'datetime':
                        databases.create_datetime_attribute(
                            database_id=config.database_id,
                            collection_id=collection_config['id'],
                            key=attr['key'],
                            required=attr['required'],
                            default=attr.get('default', None),
                            array=False
                        )
                    elif attr['type'] == 'enum':
                        databases.create_enum_attribute(
                            database_id=config.database_id,
                            collection_id=collection_config['id'],
                            key=attr['key'],
                            elements=attr['elements'],
                            required=attr['required'],
                            default=attr.get('default', None),
                            array=False
                        )
                
                # Wait a moment for attributes to be created
                import time
                time.sleep(2)
                
                # Create indexes
                for index in collection_config['indexes']:
                    print(f"  Creating index '{index['key']}'...")
                    try:
                        databases.create_index(
                            database_id=config.database_id,
                            collection_id=collection_config['id'],
                            key=index['key'],
                            type=index['type'],
                            attributes=index['attributes']
                        )
                    except AppwriteException as e:
                        print(f"    Warning: Could not create index '{index['key']}': {e}")
                
                print(f"Collection '{collection_config['name']}' created successfully!")
                
            except AppwriteException as e:
                print(f"Error creating collection '{collection_config['name']}': {e}")
                continue
        
        print("\n✅ Appwrite collections setup completed!")
        print("You can now use the migrated application with Appwrite database.")
        
    except Exception as e:
        print(f"❌ Error setting up Appwrite collections: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Setting up Appwrite collections for KathaPe Business...")
    setup_collections()
