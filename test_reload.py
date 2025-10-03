#!/usr/bin/env python3

# Simple test to force reload of the module
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force reload
if 'app' in sys.modules:
    del sys.modules['app']

print("Test: Attempting to import app.py")
import app
print(f"Test: Successfully imported app module from {app.__file__}")

# Check if the bill_image function exists and get its source
import inspect
bill_image_source = inspect.getsource(app.bill_image)
if "Fetching image from Cloudinary URL" in bill_image_source:
    print("✅ New direct serving code detected in bill_image function")
else:
    print("❌ Old redirect code still present in bill_image function")

if "Successfully fetched image, serving" in bill_image_source:
    print("✅ Direct image serving functionality confirmed")
else:
    print("❌ Direct image serving not found")
