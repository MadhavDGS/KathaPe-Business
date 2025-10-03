#!/usr/bin/env python3

import os
import sys
from appwrite_utils import AppwriteDB

def main():
    # Initialize Appwrite
    appwrite_db = AppwriteDB()
    
    # Get the transaction that's causing issues
    transaction_id = "396f000f-f755-4085-b6c1-8980b38267ba"
    
    try:
        transaction = appwrite_db.get_document('transactions', transaction_id)
        
        if not transaction:
            print(f"Transaction {transaction_id} not found")
            return
        
        print(f"Transaction ID: {transaction_id}")
        print(f"Transaction keys: {list(transaction.keys())}")
        
        receipt_url = transaction.get('receipt_image_url', '')
        print(f"Receipt URL exists: {bool(receipt_url)}")
        print(f"Receipt URL type: {type(receipt_url)}")
        print(f"Receipt URL length: {len(receipt_url) if receipt_url else 0}")
        
        if receipt_url:
            print(f"Receipt URL starts with:")
            print(f"  - https://res.cloudinary.com/: {receipt_url.startswith('https://res.cloudinary.com/')}")
            print(f"  - http://res.cloudinary.com/: {receipt_url.startswith('http://res.cloudinary.com/')}")
            print(f"  - data:image/: {receipt_url.startswith('data:image/')}")
            print(f"  First 200 chars: {receipt_url[:200]}")
            
        # Check other fields as well
        for key, value in transaction.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"{key}: (string, {len(value)} chars) {value[:100]}...")
            else:
                print(f"{key}: {value}")
                
    except Exception as e:
        print(f"Error getting transaction: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
