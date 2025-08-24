#!/bin/bash

# Make all scripts executable
chmod +x verify-deployment.sh
chmod +x entrypoint.sh

# If you have other scripts, make them executable too
if [[ -f "deploy-to-railway.sh" ]]; then
    chmod +x deploy-to-railway.sh
fi

echo "✅ All scripts are now executable"
echo ""
echo "🎯 Files updated and ready for Railway deployment:"
echo "   ✅ database.py - Better error handling and connection validation"
echo "   ✅ main.py - Enhanced startup, health checks, and CORS"
echo "   ✅ Procfile - Railway startup command"  
echo "   ✅ railway.toml - Railway configuration"
echo "   ✅ Dockerfile - Optimized for Railway"
echo "   ✅ .env.production - Production environment template"
echo "   ✅ entrypoint.sh - Enhanced startup script"
echo "   ✅ verify-deployment.sh - Deployment verification"
echo ""
echo "🚀 Next steps:"
echo "1. Update .env.production with your actual Neon.tech DATABASE_URL"
echo "2. Generate secure secrets for JWT and internal tokens"
echo "3. Set environment variables in Railway dashboard"
echo "4. Deploy using 'railway up' or Railway dashboard"
