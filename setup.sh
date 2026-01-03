#!/bin/bash

# Crowdfunding Project Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "🚀 Crowdfunding Project Setup"
echo "=============================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed."
    echo "📦 Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ UV installed successfully"
    echo ""
    echo "⚠️  Please restart your terminal and run this script again."
    exit 0
fi

echo "✅ UV is installed"
echo ""

# Sync Python dependencies
echo "📦 Installing Python dependencies..."
uv sync
echo "✅ Python dependencies installed"
echo ""

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm is not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js/npm is installed"
echo ""

# Install Tailwind dependencies
echo "📦 Installing Tailwind CSS dependencies..."
cd theme/static_src
npm install
cd ../..
echo "✅ Tailwind CSS dependencies installed"
echo ""

# Run migrations
echo "🗄️  Running database migrations..."
uv run python manage.py migrate
echo "✅ Database migrations completed"
echo ""

# Set up .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and set your admin credentials"
    echo "   Then run: uv run python manage.py create_admin"
    echo ""
else
    echo "ℹ️  .env file already exists"
    echo ""
fi

# Ask if user wants to create admin account
read -p "❓ Do you want to create an admin account now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if .env has admin credentials
    if grep -q "ADMIN_USERNAME=admin" .env && grep -q "ADMIN_PASSWORD=changeme123" .env; then
        echo "⚠️  WARNING: Using default credentials from .env.example"
        echo "   Please change these in production!"
        echo ""
    fi

    echo "👤 Creating admin account..."
    uv run python manage.py create_admin
    echo ""
fi

echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Start the development server:"
echo "      uv run honcho -f Procfile.tailwind start"
echo ""
echo "   2. Open your browser to:"
echo "      http://localhost:8000"
echo ""
echo "   3. Access admin panel at:"
echo "      http://localhost:8000/admin/"
echo ""
echo "   4. Run tests:"
echo "      uv run python manage.py test"
echo ""
echo "Happy coding! 🎉"
