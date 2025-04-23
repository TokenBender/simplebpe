#!/bin/bash

# Initialize git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: BPE algorithm implementation"

# Instructions for pushing to a remote repository
echo ""
echo "Repository initialized with initial commit."
echo ""
echo "To push to GitHub, create a new repository on GitHub and then run:"
echo "git remote add origin https://github.com/yourusername/bpe-algorithm.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "Replace 'yourusername' with your actual GitHub username and 'bpe-algorithm' with your repository name."