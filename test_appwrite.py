"""
Simple Appwrite Connection Test with Multiple Endpoints
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from appwrite.client import Client
    from appwrite.services.databases import Databases
    
    print("✅ Appwrite SDK imported successfully")
    
    # List of possible endpoints to try
    endpoints = [
        'https://cloud.appwrite.io/v1',
        'https://eu-central-1.appwrite.cloud/v1',
        'https://us-east-1.appwrite.cloud/v1',
        'https://ap-south-1.appwrite.cloud/v1',
        'https://ap-southeast-1.appwrite.cloud/v1'
    ]
    
    project_id = os.environ.get('APPWRITE_PROJECT_ID')
    api_key = os.environ.get('APPWRITE_API_KEY')
    database_id = os.environ.get('APPWRITE_DATABASE_ID', 'kathape_business')
    
    print(f"🆔 Project ID: {project_id}")
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🗄️ Database ID: {database_id}")
    
    for endpoint in endpoints:
        print(f"\n🌍 Trying endpoint: {endpoint}")
        
        try:
            # Initialize client
            client = Client()
            client.set_endpoint(endpoint)
            client.set_project(project_id)
            client.set_key(api_key)
            
            databases = Databases(client)
            
            # Try to list databases to verify connection
            db_list = databases.list()
            print(f"✅ SUCCESS! Connection works with {endpoint}")
            print(f"   Found {db_list['total']} databases")
            
            # Update .env file with working endpoint
            with open('.env', 'r') as f:
                content = f.read()
            
            content = content.replace('APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1', f'APPWRITE_ENDPOINT={endpoint}')
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print(f"✅ Updated .env file with working endpoint: {endpoint}")
            break
            
        except Exception as e:
            print(f"❌ Failed with {endpoint}: {e}")
            continue
    else:
        print("❌ No working endpoint found. Please check your project ID and API key.")
        exit(1)
    
    print("🎉 Appwrite connection test passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
