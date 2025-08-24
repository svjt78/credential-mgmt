#!/usr/bin/env sh
# entrypoint.sh - Updated for Railway deployment

echo "🚀 Starting Credential Management Service..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set"
    echo "Please configure DATABASE_URL in Railway dashboard"
    exit 1
fi

echo "✅ DATABASE_URL is configured"

# Test database connection and create tables
echo "🔧 Setting up database..."
python - <<'EOF'
try:
    from database import engine, Base, test_connection
    import models
    
    print("Testing database connection...")
    if test_connection():
        print("Creating/verifying database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database setup completed successfully")
    else:
        print("❌ Database connection failed")
        exit(1)
except Exception as e:
    print(f"❌ Database setup error: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "❌ Database setup failed"
    exit 1
fi

echo "🎉 Starting FastAPI application..."

# Use PORT environment variable from Railway, fallback to 8000
export PORT=${PORT:-8000}

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port $PORT
