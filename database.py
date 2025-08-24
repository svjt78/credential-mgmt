# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DATABASE_URL with fallback and validation
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Try alternative environment variable names Railway might use
    DATABASE_URL = os.getenv("DB_URL") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_CONNECTION_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please configure it in Railway dashboard under Variables tab."
    )

print(f"Connecting to database: {DATABASE_URL[:50]}...")  # Log partial URL for debugging

# Create engine with connection pooling optimized for Railway
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
    echo=False           # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Test database connection
def test_connection():
    try:
        with engine.connect() as connection:
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
