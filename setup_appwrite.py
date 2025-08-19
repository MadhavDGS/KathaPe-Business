"""
Appwrite Database Setup Script
Run this script to create the required collections in your Appwrite project
"""
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.permission import Permission
from appwrite.role import Role
import os

def setup_appwrite_collections():
    """Setup all required collections in Appwrite"""
    
    # Initialize client
    client = Client()
    client.set_endpoint(os.environ.get('APPWRITE_ENDPOINT', 'https://cloud.appwrite.io/v1'))
    client.set_project(os.environ.get('APPWRITE_PROJECT_ID'))
    client.set_key(os.environ.get('APPWRITE_API_KEY'))
    
    databases = Databases(client)
    database_id = os.environ.get('APPWRITE_DATABASE_ID', '68a41b540008cab81589')
    
    try:
        # Use existing database - no need to create
        print(f"✅ Using existing database: {database_id}")
        
        # Verify database exists
        try:
            database = databases.get(database_id)
            print(f"✅ Database '{database['name']}' found and accessible!")
        except Exception as e:
            print(f"❌ Cannot access database: {e}")
            return

        # Collection configurations
        collections_config = [
            {
                'id': 'users',
                'name': 'Users',
                'attributes': [
                    {'key': 'name', 'type': 'string', 'size': 255, 'required': True},
                    {'key': 'phone_number', 'type': 'string', 'size': 20, 'required': True},
                    {'key': 'email', 'type': 'string', 'size': 255, 'required': False},
                    {'key': 'user_type', 'type': 'string', 'size': 50, 'required': True},
                    {'key': 'password', 'type': 'string', 'size': 255, 'required': True},
                    {'key': 'profile_photo_url', 'type': 'string', 'size': 500, 'required': False},
                    {'key': 'is_active', 'type': 'boolean', 'required': True, 'default': True},
                    {'key': 'created_at', 'type': 'datetime', 'required': True},
                    {'key': 'updated_at', 'type': 'datetime', 'required': True}
                ]
            },
            {
                'id': 'businesses',
                'name': 'Businesses',
                'attributes': [
                    {'key': 'user_id', 'type': 'string', 'size': 50, 'required': True},
                    {'key': 'name', 'type': 'string', 'size': 255, 'required': True},
                    {'key': 'description', 'type': 'string', 'size': 1000, 'required': False},
                    {'key': 'business_type', 'type': 'string', 'size': 100, 'required': False},
                    {'key': 'address', 'type': 'string', 'size': 500, 'required': False},
                    {'key': 'city', 'type': 'string', 'size': 100, 'required': False},
                    {'key': 'state', 'type': 'string', 'size': 100, 'required': False},
                    {'key': 'pincode', 'type': 'string', 'size': 10, 'required': False},
                    {'key': 'access_pin', 'type': 'string', 'size': 10, 'required': True},
                    {'key': 'qr_code_data', 'type': 'string', 'size': 1000, 'required': False},
                    {'key': 'is_active', 'type': 'boolean', 'required': True, 'default': True},
                    {'key': 'created_at', 'type': 'datetime', 'required': True},
                    {'key': 'updated_at', 'type': 'datetime', 'required': True}
                ]
            },
            {
                'id': 'customers',
                'name': 'Customers',
                'attributes': [
                    {'key': 'business_id', 'type': 'string', 'size': 50, 'required': True},
                    {'key': 'name', 'type': 'string', 'size': 255, 'required': True},
                    {'key': 'phone', 'type': 'string', 'size': 20, 'required': True},
                    {'key': 'email', 'type': 'string', 'size': 255, 'required': False},
                    {'key': 'address', 'type': 'string', 'size': 500, 'required': False},
                    {'key': 'balance', 'type': 'double', 'required': True, 'default': 0.0},
                    {'key': 'created_at', 'type': 'datetime', 'required': True},
                    {'key': 'updated_at', 'type': 'datetime', 'required': True}
                ]
            },
            {
                'id': 'transactions',
                'name': 'Transactions',
                'attributes': [
                    {'key': 'business_id', 'type': 'string', 'size': 50, 'required': True},
                    {'key': 'customer_id', 'type': 'string', 'size': 50, 'required': True},
                    {'key': 'amount', 'type': 'double', 'required': True},
                    {'key': 'transaction_type', 'type': 'string', 'size': 20, 'required': True},
                    {'key': 'description', 'type': 'string', 'size': 1000, 'required': False},
                    {'key': 'receipt_image_url', 'type': 'string', 'size': 100000, 'required': False},  # Large for base64
                    {'key': 'created_at', 'type': 'datetime', 'required': True},
                    {'key': 'updated_at', 'type': 'datetime', 'required': True}
                ]
            },
            {
                'id': 'customer_credits',
                'name': 'Customer Credits',
                'attributes': [
                    {'key': 'business_id', 'type': 'string', 'size': 50, 'required': True},
                    {'key': 'customer_id', 'type': 'string', 'size': 50, 'required': True},
                    {'key': 'amount', 'type': 'double', 'required': True},
                    {'key': 'description', 'type': 'string', 'size': 1000, 'required': False},
                    {'key': 'created_at', 'type': 'datetime', 'required': True},
                    {'key': 'updated_at', 'type': 'datetime', 'required': True}
                ]
            },
            {
                'id': 'reminders',
                'name': 'Reminders',
                'attributes': [
                    {'key': 'business_id', 'type': 'string', 'size': 50, 'required': True},
                    {'key': 'customer_id', 'type': 'string', 'size': 50, 'required': True},
                    {'key': 'amount', 'type': 'double', 'required': True},
                    {'key': 'message', 'type': 'string', 'size': 1000, 'required': False},
                    {'key': 'status', 'type': 'string', 'size': 20, 'required': True},
                    {'key': 'sent_at', 'type': 'datetime', 'required': False},
                    {'key': 'created_at', 'type': 'datetime', 'required': True}
                ]
            }
        ]

        # Create collections
        for config in collections_config:
            try:
                # Create collection
                collection = databases.create_collection(
                    database_id=database_id,
                    collection_id=config['id'],
                    name=config['name'],
                    permissions=[
                        Permission.read(Role.any()),
                        Permission.write(Role.any()),
                        Permission.create(Role.any()),
                        Permission.update(Role.any()),
                        Permission.delete(Role.any())
                    ]
                )
                print(f"✅ Collection '{config['name']}' created!")
                
                # Create attributes
                for attr in config['attributes']:
                    try:
                        if attr['type'] == 'string':
                            databases.create_string_attribute(
                                database_id=database_id,
                                collection_id=config['id'],
                                key=attr['key'],
                                size=attr['size'],
                                required=attr['required'],
                                default=attr.get('default')
                            )
                        elif attr['type'] == 'boolean':
                            databases.create_boolean_attribute(
                                database_id=database_id,
                                collection_id=config['id'],
                                key=attr['key'],
                                required=attr['required'],
                                default=attr.get('default', False)
                            )
                        elif attr['type'] == 'double':
                            databases.create_float_attribute(
                                database_id=database_id,
                                collection_id=config['id'],
                                key=attr['key'],
                                required=attr['required'],
                                default=attr.get('default')
                            )
                        elif attr['type'] == 'datetime':
                            databases.create_datetime_attribute(
                                database_id=database_id,
                                collection_id=config['id'],
                                key=attr['key'],
                                required=attr['required'],
                                default=attr.get('default')
                            )
                        
                        print(f"  ✅ Attribute '{attr['key']}' created")
                        
                    except Exception as e:
                        if "already exists" in str(e):
                            print(f"  ✅ Attribute '{attr['key']}' already exists")
                        else:
                            print(f"  ❌ Error creating attribute '{attr['key']}': {e}")
                
            except Exception as e:
                if "already exists" in str(e):
                    print(f"✅ Collection '{config['name']}' already exists!")
                else:
                    print(f"❌ Error creating collection '{config['name']}': {e}")

        print("\n🎉 Appwrite setup completed!")
        print("\n📝 Next steps:")
        print("1. Set these environment variables in Render:")
        print("   APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1")
        print("   APPWRITE_PROJECT_ID=your_project_id")
        print("   APPWRITE_API_KEY=your_api_key")
        print("   APPWRITE_DATABASE_ID=kathape_business")
        print("2. Deploy your updated application to Render")

    except Exception as e:
        print(f"❌ Setup failed: {e}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🚀 Setting up Appwrite collections...")
    setup_appwrite_collections()
