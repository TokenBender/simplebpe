#!/bin/bash

# This script helps you push your local repository to a remote repository
# Usage: ./push_to_remote.sh <remote_url>

if [ $# -eq 0 ]; then
    echo "Error: Please provide the remote repository URL"
    echo "Usage: ./push_to_remote.sh <remote_url>"
    echo "Example: ./push_to_remote.sh https://github.com/yourusername/bpe-algorithm.git"
    exit 1
fi

REMOTE_URL=$1

# Add the remote repository
git remote add origin $REMOTE_URL

# Rename the branch to main if it's not already
git branch -M main

# Push to the remote repository
git push -u origin main

echo ""
echo "Repository pushed to $REMOTE_URL"
echo "You can now clone it using: git clone $REMOTE_URL"