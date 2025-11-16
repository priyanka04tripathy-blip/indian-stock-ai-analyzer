# How to Push to GitHub

## Step 1: Create a New Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `indian-stock-ai-analyzer` (or any name you prefer)
3. Description: "Indian Stock AI Analyzer with Groq AI and Serper API"
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

## Step 2: Push Your Code

Run these commands in your terminal:

```bash
cd /Users/priyanka/Documents/Cursor/stock

# Add your GitHub repository as remote
git remote add origin https://github.com/priyanka04tripathy-blip/indian-stock-ai-analyzer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note**: Replace `indian-stock-ai-analyzer` with your actual repository name if different.

## Step 3: Authentication

If prompted for authentication:
- Use a **Personal Access Token** (not your password)
- Create one at: https://github.com/settings/tokens
- Select scopes: `repo` (full control of private repositories)

## Alternative: Using SSH

If you prefer SSH:

```bash
git remote add origin git@github.com:priyanka04tripathy-blip/indian-stock-ai-analyzer.git
git push -u origin main
```

## Verify

Check your repository at:
https://github.com/priyanka04tripathy-blip/indian-stock-ai-analyzer

