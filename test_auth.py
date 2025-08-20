#!/usr/bin/env python3
"""
Test Registration and Login
Quick test to verify registration and login functionality works with Appwrite
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_registration():
    """Test user registration"""
    print("🧪 Testing Registration...")
    
    registration_data = {
        'name': 'Test Business',
        'phone': '9999999999',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", data=registration_data, allow_redirects=False)
        print(f"Registration Response Status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect means success
            print("✅ Registration appears successful (redirected)")
            return True
        elif response.status_code == 200:
            # Check if there's an error message in the response
            if "Phone number already registered" in response.text:
                print("ℹ️  Phone number already registered (expected if running multiple times)")
                return True
            elif "Registration successful" in response.text:
                print("✅ Registration successful")
                return True
            else:
                print("❌ Registration failed - check response")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Registration test error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n🧪 Testing Login...")
    
    login_data = {
        'phone': '9999999999',
        'password': 'testpass123'
    }
    
    try:
        session = requests.Session()
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        print(f"Login Response Status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect means success
            print("✅ Login appears successful (redirected)")
            return True
        elif response.status_code == 200:
            if "Successfully logged in" in response.text:
                print("✅ Login successful")
                return True
            elif "Invalid phone number or password" in response.text:
                print("❌ Login failed - invalid credentials")
                return False
            else:
                print("❌ Login failed - check response")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

def main():
    print("🚀 Testing Registration and Login Functionality...")
    print("=" * 50)
    
    # Test registration
    registration_success = test_registration()
    
    # Test login
    login_success = test_login()
    
    print("\n" + "=" * 50)
    if registration_success and login_success:
        print("🎉 All tests passed! Registration and login are working.")
    else:
        print("⚠️  Some tests failed. Check the application logs.")
        print("Common issues:")
        print("- Appwrite connection problems")
        print("- Database not properly initialized")
        print("- Missing environment variables")

if __name__ == "__main__":
    main()
