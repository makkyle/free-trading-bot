#!/bin/bash

# ============================================================================
# ENSEMBLE TRADING DASHBOARD - ONE-CLICK DEPLOYMENT SETUP
# ============================================================================
# This script automates setup for deploying to Streamlit Cloud or alternatives

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ENSEMBLE TRADING DASHBOARD - DEPLOYMENT SETUP               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found. Please install Git first.${NC}"
    exit 1
fi

# Initialize git if not already done
if [ ! -d .git ]; then
    echo -e "${YELLOW}📦 Initializing Git repository...${NC}"
    git init
    git config user.email "trader@ensemble.local"
    git config user.name "Ensemble Trader"
fi

# Add all files
echo -e "${YELLOW}📝 Staging files...${NC}"
git add .

# Commit
if git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}ℹ️  No changes to commit${NC}"
else
    git commit -m "Add ensemble trading dashboard - interactive backtesting interface"
fi

echo ""
echo -e "${GREEN}✅ Repository ready!${NC}"
echo ""

# Instructions
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "${YELLOW}Option 1: Deploy to Streamlit Cloud (Recommended)${NC}"
echo "  1. Create a GitHub account at github.com"
echo "  2. Create a new repository named 'free-trading-bot'"
echo "  3. Push this repo to GitHub:"
echo -e "${BLUE}     git remote add origin https://github.com/YOUR_USERNAME/free-trading-bot.git${NC}"
echo -e "${BLUE}     git branch -M main${NC}"
echo -e "${BLUE}     git push -u origin main${NC}"
echo "  4. Visit: https://streamlit.io/cloud"
echo "  5. Click 'New app' → Select your repo → Deploy"
echo ""

echo -e "${YELLOW}Option 2: Deploy to Hugging Face Spaces (Easiest)${NC}"
echo "  1. Visit: https://huggingface.co/spaces"
echo "  2. Click 'Create new Space' → Select 'Streamlit'"
echo "  3. Connect your GitHub account"
echo "  4. Select this repository → Auto-deploys in 2 minutes"
echo ""

echo -e "${YELLOW}Option 3: Deploy to Render.com${NC}"
echo "  1. Visit: https://render.com"
echo "  2. Click 'New +' → 'Web Service'"
echo "  3. Connect your GitHub repo"
echo "  4. Set build: ${BLUE}pip install -r requirements.txt${NC}"
echo "  5. Set start: ${BLUE}streamlit run app.py --server.port=10000 --server.address=0.0.0.0${NC}"
echo "  6. Deploy"
echo ""

echo -e "${YELLOW}Option 4: Run Locally${NC}"
echo -e "${BLUE}  streamlit run app.py${NC}"
echo "  Then open: http://localhost:8501"
echo ""

echo -e "${GREEN}🎉 Happy backtesting!${NC}"
