#!/bin/bash

REPO_NAME="indian-stock-ai-analyzer"
GITHUB_USER="priyanka04tripathy-blip"
DESCRIPTION="Indian Stock AI Analyzer with Groq AI and Serper API"

echo "🚀 Creating GitHub repository and pushing code..."
echo ""

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN not found in environment."
    echo ""
    echo "To create the repository automatically, you need a GitHub Personal Access Token."
    echo "1. Create one at: https://github.com/settings/tokens"
    echo "2. Select scope: 'repo' (full control)"
    echo "3. Run: export GITHUB_TOKEN='your-token-here'"
    echo "4. Then run this script again"
    echo ""
    echo "Alternatively, create the repository manually:"
    echo "1. Go to: https://github.com/new"
    echo "2. Name: $REPO_NAME"
    echo "3. Description: $DESCRIPTION"
    echo "4. Don't initialize with README"
    echo "5. Then run: ./push.sh $REPO_NAME"
    echo ""
    exit 1
fi

# Create repository via GitHub API
echo "📦 Creating repository: $GITHUB_USER/$REPO_NAME"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"description\":\"$DESCRIPTION\",\"private\":false}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 201 ]; then
    echo "✅ Repository created successfully!"
elif [ "$HTTP_CODE" -eq 422 ]; then
    echo "ℹ️  Repository might already exist, continuing..."
else
    echo "❌ Error creating repository (HTTP $HTTP_CODE)"
    echo "Response: $BODY"
    echo ""
    echo "Please create the repository manually at: https://github.com/new"
    echo "Name: $REPO_NAME"
    exit 1
fi

# Set up git remote
echo ""
echo "🔗 Setting up git remote..."
cd "$(dirname "$0")"
git remote remove origin 2>/dev/null
git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git

# Set branch to main
git branch -M main

# Push to GitHub
echo "📤 Pushing code to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "🔗 View your repository at: https://github.com/$GITHUB_USER/$REPO_NAME"
else
    echo ""
    echo "❌ Error pushing to GitHub."
    echo "You may need to authenticate. Try:"
    echo "  git push -u origin main"
    echo "And use your Personal Access Token as the password."
fi

