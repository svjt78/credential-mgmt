#!/bin/bash

# ===========================================
# Railway Environment Variable Setup Guide
# ===========================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Railway Environment Variable Setup${NC}"
echo "========================================"

echo -e "${YELLOW}📋 Step-by-step Railway dashboard setup:${NC}"
echo ""

echo -e "${BLUE}1. Go to your Railway project dashboard${NC}"
echo "   https://railway.app/dashboard"
echo ""

echo -e "${BLUE}2. Click on your 'digitaldossier-credentials' service${NC}"
echo ""

echo -e "${BLUE}3. Go to 'Variables' tab${NC}"
echo ""

echo -e "${BLUE}4. Add these EXACT variable names and values:${NC}"
echo ""

# Check if .env.production exists and show values
if [[ -f ".env.production" ]]; then
    echo -e "${GREEN}From your .env.production file:${NC}"
    echo "----------------------------------------"
    
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ $key =~ ^#.*$ ]] || [[ -z "$key" ]]; then
            continue
        fi
        
        # Remove any quotes from the value
        value=$(echo "$value" | sed 's/^["'"'"']//;s/["'"'"']$//')
        
        # Show the key-value pair
        echo -e "${YELLOW}Variable Name:${NC} $key"
        if [[ $key == *"SECRET"* ]] || [[ $key == *"TOKEN"* ]] || [[ $key == *"PASSWORD"* ]]; then
            echo -e "${YELLOW}Variable Value:${NC} ${value:0:20}... (truncated for security)"
        else
            echo -e "${YELLOW}Variable Value:${NC} $value"
        fi
        echo ""
        
    done < .env.production
else
    echo -e "${RED}❌ .env.production file not found${NC}"
    echo ""
    echo -e "${YELLOW}Required variables to set in Railway dashboard:${NC}"
    echo ""
    echo "DATABASE_URL = postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/credentialdb?sslmode=require"
    echo "SECRET_KEY = (generate with: openssl rand -base64 32)"
    echo "JWT_SECRET = (same as SECRET_KEY)"
    echo "ALGORITHM = HS256"
    echo "FRONTEND_BASE_URL = https://digitaldossier.us"
    echo "EMAIL_VERIFICATION_TTL_HOURS = 24"
    echo "INTERNAL_SERVICE_TOKEN = (generate with: openssl rand -hex 32)"
fi

echo ""
echo -e "${BLUE}5. After adding variables, trigger a new deployment:${NC}"
echo "   - Click 'Deploy' button in Railway dashboard"
echo "   - OR run: railway up --detach"
echo ""

echo -e "${BLUE}6. Monitor deployment logs:${NC}"
echo "   - Stay on Railway dashboard"
echo "   - Click 'View Logs' to see startup messages"
echo "   - Look for our debug messages"
echo ""

echo -e "${YELLOW}🚨 Common Railway Issues & Solutions:${NC}"
echo ""
echo -e "${RED}Issue:${NC} Variables not available during build"
echo -e "${GREEN}Solution:${NC} Set variables as 'Runtime' not 'Build' variables"
echo ""
echo -e "${RED}Issue:${NC} Variable names case-sensitive"
echo -e "${GREEN}Solution:${NC} Use EXACT case: DATABASE_URL (not database_url)"
echo ""
echo -e "${RED}Issue:${NC} Values with special characters"
echo -e "${GREEN}Solution:${NC} Don't use quotes around values in Railway dashboard"
echo ""

echo -e "${BLUE}🔍 Debugging Steps:${NC}"
echo ""
echo "1. After deployment, check logs for our debug messages"
echo "2. Look for 'Found database URL in environment variable: ...' message"
echo "3. If still failing, enable debug endpoint by adding:"
echo "   ENABLE_DEBUG = true"
echo "4. Then visit: https://your-railway-url.railway.app/debug/env"
echo ""

echo -e "${GREEN}✅ Follow these steps and your deployment should work!${NC}"
