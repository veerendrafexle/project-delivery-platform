#!/bin/bash
# Git setup and push script for AI Delivery Platform

set -e

echo "🔧 Setting up Git repository..."

# Initialize repository
git init

# Configure git user
git config user.email "${GIT_EMAIL:-dev@delivery.local}"
git config user.name "${GIT_NAME:-AI Delivery Platform}"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AI Delivery Platform

- Modular architecture with 10 core modules
- AI-powered requirement extraction with retry logic (3 attempts)
- Schema validation and deduplication
- Enhanced hallucination detection
- Streamlit UI for BRD generation
- Comprehensive error handling and timeouts
- Environment variable configuration
- Sample data and workflows"

echo "✅ Git repository initialized with initial commit"
echo ""
echo "📤 To push to a remote repository:"
echo "  1. Create a repo on GitHub/GitLab/Bitbucket"
echo "  2. Add remote: git remote add origin <your-repo-url>"
echo "  3. Push: git push -u origin main"
echo ""
echo "📊 Git log:"
git log --oneline
