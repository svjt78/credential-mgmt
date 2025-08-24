# ===========================================
# Railway Deployment Script
# ===========================================
# File: deploy-to-railway.sh

#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚂 Railway Deployment Script for Credentials Service${NC}"
echo "=================================================="

# Check if Railway CLI is installed
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        echo -e "${RED}❌ Railway CLI not found${NC}"
        echo -e "${YELLOW}Installing Railway CLI...${NC}"
        
        # Install Railway CLI
        curl -fsSL https://railway.app/install.sh | sh
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Failed to install Railway CLI${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ Railway CLI installed${NC}"
    else
        echo -e "${GREEN}✅ Railway CLI found${NC}"
    fi
}

# Login to Railway
railway_login() {
    echo -e "${YELLOW}🔐 Logging into Railway...${NC}"
    railway login
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Railway login failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Railway login successful${NC}"
}

# Create new Railway project
create_railway_project() {
    echo -e "${YELLOW}🚀 Creating Railway project...${NC}"
    
    # Navigate to credentials service directory
    cd /Users/SD60006/Documents/Rest/apps/apps/credentials/credential_service
    
    # Initialize Railway project
    railway init digitaldossier-credentials
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create Railway project${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Railway project created: digitaldossier-credentials${NC}"
}

# Set environment variables
set_environment_variables() {
    echo -e "${YELLOW}⚙️  Setting environment variables...${NC}"
    
    # Check if production env file exists
    if [ ! -f ".env.production" ]; then
        echo -e "${RED}❌ .env.production file not found${NC}"
        echo "Please create .env.production with your Neon.tech connection string and other production variables"
        exit 1
    fi
    
    # Read variables from production env file and set them in Railway
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ $key =~ ^#.*$ ]] || [[ -z "$key" ]]; then
            continue
        fi
        
        # Remove any quotes from the value
        value=$(echo "$value" | sed 's/^["'"'"']//;s/["'"'"']$//')
        
        echo "Setting $key..."
        railway variables set "$key=$value"
        
    done < .env.production
    
    echo -e "${GREEN}✅ Environment variables set${NC}"
}

# Deploy to Railway
deploy_application() {
    echo -e "${YELLOW}🚀 Deploying to Railway...${NC}"
    
    # Create production Dockerfile if it doesn't exist
    if [ ! -f "Dockerfile.prod" ]; then
        echo -e "${YELLOW}📝 Creating production Dockerfile...${NC}"
        
        cat > Dockerfile.prod << 'EOF'
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=10)" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
        
        echo -e "${GREEN}✅ Production Dockerfile created${NC}"
    fi
    
    # Deploy
    railway up
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Railway deployment failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Railway deployment successful${NC}"
}

# Get deployment information
get_deployment_info() {
    echo -e "${YELLOW}📋 Getting deployment information...${NC}"
    
    # Get the deployment URL
    RAILWAY_URL=$(railway status | grep -o 'https://[^[:space:]]*')
    
    if [ -n "$RAILWAY_URL" ]; then
        echo -e "${GREEN}🎉 Deployment successful!${NC}"
        echo ""
        echo -e "${BLUE}📍 Your credentials service is deployed at:${NC}"
        echo -e "${GREEN}   $RAILWAY_URL${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Important: Update your blog app's AUTH_API_BASE to:${NC}"
        echo -e "${GREEN}   $RAILWAY_URL${NC}"
        echo ""
        echo -e "${YELLOW}🧪 Test your API:${NC}"
        echo "   curl $RAILWAY_URL"
        echo ""
    else
        echo -e "${RED}❌ Could not retrieve deployment URL${NC}"
        echo "Check Railway dashboard for deployment status"
    fi
}

# Main execution
main() {
    echo -e "${GREEN}Starting Railway deployment...${NC}"
    
    check_railway_cli
    railway_login
    create_railway_project
    set_environment_variables
    deploy_application
    get_deployment_info
    
    echo -e "${GREEN}🎉 Railway deployment completed!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Update blog app's AUTH_API_BASE environment variable"
    echo "2. Deploy blog app to Vercel"
    echo "3. Test end-to-end authentication flow"
}

# Usage information
usage() {
    echo "Usage: $0"
    echo ""
    echo "Prerequisites:"
    echo "1. Create .env.production file with all required environment variables"
    echo "2. Ensure Neon.tech database is set up and accessible"
    echo "3. Have Railway account ready"
    echo ""
    echo "This script will:"
    echo "- Install Railway CLI if needed"
    echo "- Create Railway project"
    echo "- Set environment variables from .env.production"
    echo "- Deploy the FastAPI credentials service"
    echo "- Provide deployment URL for blog app configuration"
}

# Check for help flag
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    usage
    exit 0
fi

# Run main function
main "$@"