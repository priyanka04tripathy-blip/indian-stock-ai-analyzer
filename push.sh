#!/bin/bash
# Script to push stock project to GitHub
# Usage: ./push.sh <repository-name>

REPO_NAME=${1:-"indian-stock-ai-analyzer"}
GITHUB_USER="priyanka04tripathy-blip"

echo "🚀 Pushing to GitHub..."
echo "Repository: $GITHUB_USER/$REPO_NAME"

# Add remote (remove if exists first)
git remote remove origin 2>/dev/null
git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git

# Set branch to main
git branch -M main

# Push to GitHub
echo "📤 Pushing code to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo "🔗 View your repository at: https://github.com/$GITHUB_USER/$REPO_NAME"
else
    echo "❌ Error pushing to GitHub. Make sure:"
    echo "   1. Repository exists on GitHub"
    echo "   2. You have authentication set up (Personal Access Token)"
    echo "   3. Repository name is correct: $REPO_NAME"
fi

