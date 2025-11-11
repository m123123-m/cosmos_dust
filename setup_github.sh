#!/bin/bash
# Script to connect and push to GitHub repository

echo "Setting up GitHub connection for cosmos_dust..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Add remote if it doesn't exist
if ! git remote | grep -q "origin"; then
    echo "Adding GitHub remote..."
    git remote add origin https://github.com/m123123-m/cosmos_dust.git
fi

# Add all files
echo "Adding files..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "No changes to commit."
else
    echo "Committing changes..."
    git commit -m "Initial commit: Cosmic Dust Trajectory Calculator web application"
fi

echo ""
echo "To push to GitHub, run:"
echo "  git push -u origin main"
echo ""
echo "Or if your default branch is 'master':"
echo "  git push -u origin master"
echo ""
echo "If you need to set the branch name:"
echo "  git branch -M main"
echo "  git push -u origin main"

