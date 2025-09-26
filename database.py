# database.py
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """
    Get DATABASE_URL with multiple fallbacks for Railway deployment
    """
    # Try multiple environment variable names
    possible_names = [
        "DATABASE_URL",
        "DB_URL", 
        "POSTGRES_URL",
        "DATABASE_CONNECTION_URL",
        "POSTGRESQL_URL"
    ]
    
    database_url = None
    
    for name in possible_names:
        database_url = os.getenv(name)
        if database_url:
            print(f"✅ Found database URL in environment variable: {name}")
            break
    
    if not database_url:
        print("❌ Environment variables available:")
        # Debug: Print all environment variables that contain 'URL' or 'DB'
        for key, value in os.environ.items():
            if any(keyword in key.upper() for keyword in ['URL', 'DB', 'POSTGRES']):
                # Only show first 30 chars for security
                print(f"   {key} = {value[:30]}...")
        
        print("\n❌ Available environment variables:")
        for key in sorted(os.environ.keys()):
            print(f"   {key}")
            
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please configure it in Railway dashboard under Variables tab. "
            f"Tried these variable names: {', '.join(possible_names)}"
        )
    
    return database_url

# Get DATABASE_URL with robust error handling
try:
    DATABASE_URL = get_database_url()
    print(f"🔗 Connecting to database: {DATABASE_URL[:50]}...")  # Log partial URL for debugging
except ValueError as e:
    print(f"❌ Database configuration error: {e}")
    # In Railway, we want to fail fast if DB config is wrong
    sys.exit(1)

# Create engine with connection pooling optimized for Railway
try:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections every hour
        echo=False,          # Set to True for SQL debugging
        connect_args={
            "sslmode": "disable" if "localhost" in DATABASE_URL or "credential-db" in DATABASE_URL else "require",
        }
    )
    print("✅ Database engine created successfully")
except Exception as e:
    print(f"❌ Failed to create database engine: {e}")
    sys.exit(1)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Test database connection with retry logic
def test_connection(max_retries=3):
    """Test database connection with retry logic for Railway startup"""
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                from sqlalchemy import text
                result = connection.execute(text("SELECT 1"))
                print("✅ Database connection successful")
                return True
        except Exception as e:
            print(f"❌ Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)  # Wait 2 seconds before retry
            else:
                print(f"❌ Database connection failed after {max_retries} attempts")
                return False
    return False
