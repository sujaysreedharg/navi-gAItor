#!/bin/bash
# Script to authenticate with GitHub and push navi-gAItor

echo "🔐 Authenticating with GitHub..."
gh auth login

echo "📦 Creating GitHub repository..."
gh repo create navi-gAItor --public --source=. --remote=origin --push

echo "✅ Done! Your repo is at: https://github.com/$(gh api user --jq .login)/navi-gAItor"

