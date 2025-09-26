#!/usr/bin/env python3
"""
Deploy database schema to Neon.tech
This script should be run with your Neon.tech DATABASE_URL
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from models import User

def deploy_to_neon():
    """Deploy database schema to Neon.tech"""
    
    # Get Neon DATABASE_URL from environment
    neon_url = os.getenv('NEON_DATABASE_URL')
    if not neon_url:
        print("❌ NEON_DATABASE_URL environment variable not set")
        print("Please set NEON_DATABASE_URL to your Neon.tech connection string")
        print("Example: export NEON_DATABASE_URL='postgresql://user:pass@host/db?sslmode=require'")
        sys.exit(1)
    
    print(f"🔗 Connecting to Neon.tech database...")
    
    try:
        # Create engine for Neon (requires SSL)
        engine = create_engine(
            neon_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=True,  # Show SQL commands
            connect_args={"sslmode": "require"}
        )
        
        # Test connection
        print("🔄 Testing connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to: {version}")
        
        # Create all tables
        print("🔄 Creating database tables...")
        Base = declarative_base()
        
        # Import models to register them
        from models import User
        User.__table__.create(engine, checkfirst=True)
        
        print("✅ Database schema deployed successfully to Neon.tech!")
        
        # List created tables
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"📋 Created tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    deploy_to_neon()