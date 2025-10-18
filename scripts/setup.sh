#!/bin/bash

# Setup script for Stash Agent

# Get the parent directory (project root)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Change to project root directory
cd "$PROJECT_ROOT"

echo "========================================"
echo "Gordion AI Code Review Agent Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1)
echo "Found: $PYTHON_VERSION"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check pip
echo ""
echo "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed!"
    echo "Please install pip3"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create .env file if not exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your credentials:"
    echo "   - STASH_URL"
    echo "   - STASH_USERNAME"
    echo "   - STASH_TOKEN"
    echo "   - OPENAI_API_KEY"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Create logs directory
mkdir -p logs
echo "✅ Logs directory created"

# Make scripts executable
chmod +x agent.sh
echo "✅ Scripts made executable"

echo ""
echo "========================================"
echo "Setup completed!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Test connection: python3 tests/test_connection.py"
echo "3. Test AI agent: python3 tests/test_ai.py"
echo "4. Run agent: python3 src/main.py"
echo "   or use: ./agent.sh start"
echo ""
echo "For background service:"
echo "  macOS: Follow instructions in docs/QUICKSTART.md for launchd"
echo "  Linux: Follow instructions in docs/QUICKSTART.md for systemd"
echo ""
