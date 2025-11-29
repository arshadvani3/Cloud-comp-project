#!/bin/bash

# Git Initialization Script for LLM Inference Service
# This script initializes a git repository and prepares it for GitHub

echo "🚀 Initializing Git Repository..."
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    echo "Install git first: brew install git"
    exit 1
fi

# Check if already a git repo
if [ -d ".git" ]; then
    echo "⚠️  Warning: This directory is already a git repository"
    read -p "Do you want to continue and reinitialize? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    rm -rf .git
fi

# Initialize git
echo "📦 Initializing git repository..."
git init

# Create main branch
git checkout -b main

# Add all files
echo "➕ Adding files..."
git add .

# Show what will be committed
echo ""
echo "📄 Files to be committed:"
git status --short

echo ""
echo "📊 Repository statistics:"
echo "   Total files: $(git ls-files | wc -l)"
echo "   Python files: $(git ls-files | grep '\.py$' | wc -l)"
echo "   YAML files: $(git ls-files | grep '\.yaml$' | wc -l)"
echo "   Markdown files: $(git ls-files | grep '\.md$' | wc -l)"

# Create initial commit
echo ""
read -p "📝 Create initial commit? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "Commit skipped. You can commit later with:"
    echo "  git commit -m 'Initial commit: CodeLlama inference service'"
else
    git commit -m "Initial commit: CodeLlama inference service

- Flask API with CodeLlama 7B integration
- Beautiful web interface for code generation
- Kubernetes deployment with auto-scaling (HPA)
- Comprehensive testing suite (load, spike, stress, soak)
- Multi-environment support (Ollama local, llama-cpp-python prod)
- Docker containerization
- Complete documentation"

    echo "✅ Initial commit created!"
fi

echo ""
echo "🎉 Git repository initialized!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Create a new repository on GitHub"
echo "   https://github.com/new"
echo ""
echo "2. Add remote and push:"
echo "   git remote add origin https://github.com/YOUR-USERNAME/llm-inference-service.git"
echo "   git push -u origin main"
echo ""
echo "3. (Optional) Add a description and topics on GitHub:"
echo "   Topics: kubernetes, llm, codellama, auto-scaling, flask, ai, machine-learning"
echo ""
echo "4. Share the repo link with your friend!"
echo ""
