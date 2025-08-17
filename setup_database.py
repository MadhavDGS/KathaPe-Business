#!/usr/bin/env python3
"""
Database Setup Script for KathaPe Business Application
This script helps you set up a new PostgreSQL database for the KathaPe Business app.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
import getpass

def read_sql_file(file_path):
    """Read SQL file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: SQL file '{file_path}' not found!")
        return None

def connect_to_database(db_url):
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(db_url)
        print("✅ Successfully connected to database!")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def execute_sql_script(conn, sql_content):
    """Execute SQL script"""
    try:
        with conn.cursor() as cursor:
            # Execute the SQL script
            cursor.execute(sql_content)
            conn.commit()
            print("✅ Database schema created successfully!")
            return True
    except Exception as e:
        print(f"❌ Error executing SQL script: {e}")
        conn.rollback()
        return False

def update_env_file(db_url):
    """Update .env file with new database URL"""
    try:
        env_content = f"""# KathaPe Business Application Environment Variables
DATABASE_URL={db_url}
EXTERNAL_DATABASE_URL={db_url}

# Add other environment variables as needed
# RENDER=False
# BUSINESS_PORT=5001
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file with database configuration")
        print("📝 You can modify .env file to add more environment variables")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not create .env file: {e}")

def main():
    print("🗄️  KathaPe Business Database Setup")
    print("=" * 50)
    
    # Check if schema file exists
    schema_file = 'database_schema.sql'
    if not os.path.exists(schema_file):
        print(f"❌ Error: {schema_file} not found!")
        print("Make sure you run this script from the project root directory.")
        sys.exit(1)
    
    # Get database connection details
    print("\n📝 Enter your new PostgreSQL database details:")
    print("Format: postgresql://username:password@host:port/database_name")
    print("Example: postgresql://myuser:mypass@localhost:5432/kathape_db")
    
    db_url = input("\n🔗 Database URL: ").strip()
    
    if not db_url:
        print("❌ Database URL is required!")
        sys.exit(1)
    
    # Confirm before proceeding
    print(f"\n⚠️  This will create/recreate the database schema.")
    print(f"Database: {db_url}")
    
    confirm = input("\n❓ Do you want to proceed? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Setup cancelled.")
        sys.exit(0)
    
    # Read SQL schema file
    print("\n📖 Reading database schema...")
    sql_content = read_sql_file(schema_file)
    if not sql_content:
        sys.exit(1)
    
    # Connect to database
    print("🔌 Connecting to database...")
    conn = connect_to_database(db_url)
    if not conn:
        sys.exit(1)
    
    try:
        # Execute schema creation
        print("🏗️  Creating database schema...")
        if execute_sql_script(conn, sql_content):
            print("\n🎉 Database setup completed successfully!")
            
            # Update environment file
            print("\n📄 Updating environment configuration...")
            update_env_file(db_url)
            
            print("\n✅ Next steps:")
            print("1. Update common_utils.py with your new database URL")
            print("2. Restart your Flask application")
            print("3. Register a new business account to test the setup")
            
        else:
            print("❌ Database setup failed!")
            sys.exit(1)
            
    finally:
        conn.close()
        print("🔌 Database connection closed.")

if __name__ == "__main__":
    main()
