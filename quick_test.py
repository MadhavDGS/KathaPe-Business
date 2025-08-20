"""
Quick Appwrite Endpoint Test
"""
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

project_id = os.environ.get('APPWRITE_PROJECT_ID')
api_key = os.environ.get('APPWRITE_API_KEY')

# Test endpoints quickly with HTTP requests
endpoints = [
    'https://cloud.appwrite.io/v1',
    'https://eu-central-1.appwrite.cloud/v1', 
    'https://us-east-1.appwrite.cloud/v1',
    'https://ap-south-1.appwrite.cloud/v1',
    'https://ap-southeast-1.appwrite.cloud/v1'
]

print(f"Testing endpoints for project: {project_id}")

for endpoint in endpoints:
    print(f"\n🌍 Testing: {endpoint}")
    
    try:
        # Test with a simple health check
        url = f"{endpoint}/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Health check passed for {endpoint}")
            
            # Now test database access
            db_url = f"{endpoint}/databases"
            headers = {
                'X-Appwrite-Project': project_id,
                'X-Appwrite-Key': api_key,
                'Content-Type': 'application/json'
            }
            
            db_response = requests.get(db_url, headers=headers, timeout=10)
            
            if db_response.status_code == 200:
                print(f"✅ SUCCESS! {endpoint} works perfectly!")
                print(f"   Database API accessible")
                
                # Update .env file
                with open('.env', 'r') as f:
                    content = f.read()
                
                current_endpoint = os.environ.get('APPWRITE_ENDPOINT', 'https://cloud.appwrite.io/v1')
                content = content.replace(f'APPWRITE_ENDPOINT={current_endpoint}', f'APPWRITE_ENDPOINT={endpoint}')
                
                with open('.env', 'w') as f:
                    f.write(content)
                
                print(f"✅ Updated .env with working endpoint!")
                print(f"🎉 You can now run: python setup_appwrite.py")
                break
            else:
                print(f"❌ Database access failed: {db_response.status_code}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout - endpoint too slow")
    except requests.exceptions.ConnectionError:
        print(f"🔌 Connection failed")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("\n❌ No working endpoint found!")
    print("Please check:")
    print("1. Your internet connection") 
    print("2. Your Appwrite project ID")
    print("3. Your API key permissions")
