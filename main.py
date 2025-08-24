# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from database import engine, Base, test_connection
import models  # ensures models are registered
from routes import auth as auth_routes
from routes import oauth as oauth_routes

# Test database connection on startup
print("🔧 Testing database connection...")
if not test_connection():
    print("❌ Failed to connect to database on startup")
    # In production, you might want to exit here, but Railway may retry
    # import sys; sys.exit(1)

# Create all tables in the database
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
except Exception as e:
    print(f"❌ Error creating database tables: {e}")

app = FastAPI(
    title="Credential Management Service",
    description="Authentication service for Digital Dossier",
    version="1.0.0"
)

# Configure CORS for production
frontend_url = os.getenv("FRONTEND_BASE_URL", "https://digitaldossier.us")
print(f"🌐 Configuring CORS for frontend: {frontend_url}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "https://digitaldossier.us"],  # Production URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(oauth_routes.router, tags=["oauth"])

@app.get("/")
def read_root():
    return {
        "message": "Digital Dossier Credential Management Service",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for Railway"""
    db_status = test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "service": "credential-management"
    }
