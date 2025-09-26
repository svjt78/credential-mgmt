#!/usr/bin/env python3
"""
Railway Environment Test Script
Run this to verify environment variables are working
"""

import os
import sys
from dotenv import load_dotenv

def main():
    print("🔍 Railway Environment Variable Test")
    print("=" * 40)
    
    # Load .env files
    load_dotenv()
    
    # Test DATABASE_URL specifically
    database_url = os.getenv("DATABASE_URL")
    
    print(f"DATABASE_URL found: {'✅ YES' if database_url else '❌ NO'}")
    
    if database_url:
        print(f"DATABASE_URL value: {database_url[:50]}...")
        
        # Test if it looks like a valid PostgreSQL URL
        if database_url.startswith("postgresql://"):
            print("✅ DATABASE_URL format looks correct")
        else:
            print("❌ DATABASE_URL doesn't start with postgresql://")
    
    # Show all environment variables that might be relevant
    print("\n🔍 Relevant environment variables found:")
    print("-" * 40)
    
    relevant_vars = []
    for key, value in os.environ.items():
        if any(keyword in key.upper() for keyword in ['URL', 'DB', 'POSTGRES', 'SECRET', 'TOKEN']):
            relevant_vars.append((key, value))
    
    if relevant_vars:
        for key, value in sorted(relevant_vars):
            # Truncate sensitive values
            if any(sensitive in key.upper() for sensitive in ['SECRET', 'TOKEN', 'PASSWORD']):
                display_value = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display_value = f"{value[:50]}..." if len(value) > 50 else value
            print(f"{key} = {display_value}")
    else:
        print("❌ No relevant environment variables found")
    
    print(f"\n📊 Total environment variables: {len(os.environ)}")
    
    # Test database connection if URL is available
    if database_url:
        print("\n🔗 Testing database connection...")
        try:
            from sqlalchemy import create_engine
            engine = create_engine(database_url)
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                print("✅ Database connection successful!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    
    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    main()
