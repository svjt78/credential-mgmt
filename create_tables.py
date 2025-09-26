#!/usr/bin/env python3
"""
Database table creation script for deployment
Creates all tables defined in models.py
"""
import sys
from database import engine, Base, test_connection
from models import User

def create_tables():
    """Create all database tables"""
    try:
        print("🔄 Testing database connection...")
        if not test_connection():
            print("❌ Database connection failed")
            sys.exit(1)
        
        print("🔄 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Verify tables were created
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result]
            print(f"✅ Created tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_tables()