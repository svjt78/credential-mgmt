# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

print("🚀 Starting Digital Dossier Credential Service...")
print(f"🌍 Python version: {sys.version}")
print(f"📁 Working directory: {os.getcwd()}")

# Debug environment variables
print("🔍 Checking environment variables...")
env_vars_to_check = ["DATABASE_URL", "SECRET_KEY", "FRONTEND_BASE_URL"]
for var in env_vars_to_check:
    value = os.getenv(var)
    if value:
        # Show only first 20 chars for security
        print(f"✅ {var} = {value[:20]}...")
    else:
        print(f"❌ {var} = Not set")

try:
    from database import engine, Base, test_connection
    print("✅ Database module imported successfully")
except Exception as e:
    print(f"❌ Failed to import database module: {e}")
    print("This usually means DATABASE_URL is not properly configured")
    sys.exit(1)

try:
    import models  # ensures models are registered
    print("✅ Models imported successfully")
except Exception as e:
    print(f"❌ Failed to import models: {e}")
    sys.exit(1)

try:
    from routes import auth as auth_routes
    from routes import oauth as oauth_routes
    print("✅ Routes imported successfully")
except Exception as e:
    print(f"❌ Failed to import routes: {e}")
    sys.exit(1)

# Test database connection on startup
print("🔧 Testing database connection...")
if not test_connection():
    print("❌ Failed to connect to database on startup")
    print("This is likely a DATABASE_URL configuration issue")
    # Don't exit immediately in Railway - let it retry
    print("⚠️  Continuing startup, but database operations will fail")

# Create all tables in the database
try:
    print("🗃️  Creating/verifying database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
except Exception as e:
    print(f"❌ Error creating database tables: {e}")
    print("This may indicate a database connection or permission issue")

# Create FastAPI app
app = FastAPI(
    title="Digital Dossier Credential Service",
    description="Authentication service for Digital Dossier blog platform",
    version="1.0.0",
    docs_url="/docs" if os.getenv("NODE_ENV") != "production" else None,  # Disable docs in production
    redoc_url="/redoc" if os.getenv("NODE_ENV") != "production" else None,
)

# Configure CORS for production
frontend_url = os.getenv("FRONTEND_BASE_URL", "https://digitaldossier.us")
print(f"🌐 Configuring CORS for frontend: {frontend_url}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url, 
        "https://digitaldossier.us",
        "https://www.digitaldossier.us"  # Include www variant
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(oauth_routes.router, tags=["oauth"])

@app.get("/")
def read_root():
    """Root endpoint for basic connectivity testing"""
    return {
        "message": "Digital Dossier Credential Management Service",
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("NODE_ENV", "development")
    }

@app.get("/health")
def health_check():
    """Comprehensive health check endpoint for Railway"""
    try:
        db_status = test_connection()
        
        # Check environment variables
        env_status = bool(os.getenv("DATABASE_URL") and os.getenv("SECRET_KEY"))
        
        overall_status = "healthy" if (db_status and env_status) else "unhealthy"
        
        return {
            "status": overall_status,
            "database": "connected" if db_status else "disconnected", 
            "environment": "configured" if env_status else "missing_variables",
            "service": "credential-management",
            "timestamp": os.getenv("RAILWAY_DEPLOYMENT_ID", "local")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "credential-management"
        }

@app.get("/debug/env")
def debug_environment():
    """Debug endpoint to check environment variables (remove in production)"""
    # Only show this in development or if specifically enabled
    if os.getenv("ENABLE_DEBUG") != "true":
        raise HTTPException(status_code=404, detail="Not found")
    
    env_info = {}
    for key in os.environ.keys():
        if any(keyword in key.upper() for keyword in ['URL', 'DB', 'SECRET', 'TOKEN']):
            # Only show first 10 chars for security
            env_info[key] = f"{os.environ[key][:10]}..."
    
    return {
        "environment_variables": env_info,
        "total_env_vars": len(os.environ),
        "working_directory": os.getcwd()
    }

print("✅ FastAPI application configured successfully")
print(f"🎯 Ready to serve requests on port {os.getenv('PORT', '8000')}")
