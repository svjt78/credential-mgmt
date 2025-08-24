#!/bin/bash

# ===========================================
# Railway Deployment Verification Script
# ===========================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔍 Railway Deployment Verification${NC}"
echo "===================================="

# Check current directory
if [[ ! -f "main.py" ]]; then
    echo -e "${RED}❌ Not in credentials service directory${NC}"
    echo "Please run this from: /Users/SD60006/Documents/Rest/apps/apps/credentials/credential_service"
    exit 1
fi

echo -e "${GREEN}✅ In correct directory${NC}"

# Check required files
echo -e "${YELLOW}📋 Checking required files...${NC}"

required_files=("main.py" "database.py" "requirements.txt" "Procfile" "Dockerfile" ".env.production")

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
        exit 1
    fi
done

# Check if Railway CLI is available
echo -e "${YELLOW}🚂 Checking Railway CLI...${NC}"
if command -v railway &> /dev/null; then
    echo -e "${GREEN}✅ Railway CLI installed${NC}"
    
    # Check if logged in
    if railway whoami &> /dev/null; then
        echo -e "${GREEN}✅ Railway CLI authenticated${NC}"
        
        # Check if project is linked
        if railway status &> /dev/null; then
            echo -e "${GREEN}✅ Railway project linked${NC}"
            
            # Show current status
            echo -e "${BLUE}📊 Current Railway status:${NC}"
            railway status
        else
            echo -e "${YELLOW}⚠️  No Railway project linked${NC}"
            echo "Run: railway init"
        fi
    else
        echo -e "${YELLOW}⚠️  Railway CLI not authenticated${NC}"
        echo "Run: railway login"
    fi
else
    echo -e "${RED}❌ Railway CLI not installed${NC}"
    echo "Install with: curl -fsSL https://railway.app/install.sh | sh"
fi

# Check environment variables template
echo -e "${YELLOW}🔑 Checking environment configuration...${NC}"

if [[ -f ".env.production" ]]; then
    echo -e "${GREEN}✅ .env.production exists${NC}"
    
    # Check if template values are still present
    if grep -q "your-secure-" .env.production; then
        echo -e "${YELLOW}⚠️  .env.production contains template values${NC}"
        echo "Please update the following in .env.production:"
        grep "your-secure-" .env.production
        echo ""
        echo "Generate secure values with:"
        echo "  openssl rand -base64 32  # For JWT secrets"
        echo "  openssl rand -hex 32     # For internal tokens"
    else
        echo -e "${GREEN}✅ .env.production configured${NC}"
    fi
    
    # Check for Neon.tech connection string
    if grep -q "ep-.*\..*\.aws\.neon\.tech" .env.production; then
        echo -e "${GREEN}✅ Neon.tech DATABASE_URL configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Please update DATABASE_URL with your Neon.tech connection string${NC}"
    fi
else
    echo -e "${RED}❌ .env.production missing${NC}"
    echo "Please create .env.production with your production environment variables"
fi

echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Update .env.production with actual values (DATABASE_URL, secrets)"
echo "2. In Railway Dashboard → Variables, add all variables from .env.production"
echo "3. Deploy using: railway up"
echo "4. Monitor deployment logs in Railway dashboard"

echo ""
echo -e "${GREEN}🎯 Your files are now ready for Railway deployment!${NC}"
