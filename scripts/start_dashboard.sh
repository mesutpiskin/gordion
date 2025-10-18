#!/bin/bash

# Gordion PR Agent Dashboard Launcher
# Bu script dashboard'u başlatır

echo "🚀 Starting Gordion PR Agent Dashboard..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create necessary directories
mkdir -p logs data

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from .env.example..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created. Please edit it with your credentials."
        echo ""
        echo "Opening .env file for editing..."
        ${EDITOR:-nano} .env
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Check Ollama
echo ""
echo "🔍 Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not installed!"
    echo "💡 Install with: brew install ollama"
    echo "💡 Then run: ollama serve &"
else
    echo "✅ Ollama found"
    
    # Check if Ollama is running
    if ! pgrep -x "ollama" > /dev/null; then
        echo "⚠️  Ollama is not running"
        echo "🚀 Starting Ollama..."
        ollama serve > /dev/null 2>&1 &
        sleep 2
    fi
    
    # Check if model is available
    MODEL=$(grep OLLAMA_MODEL .env | cut -d '=' -f2 | tr -d ' ')
    if [ ! -z "$MODEL" ]; then
        echo "🔍 Checking model: $MODEL"
        if ! ollama list | grep -q "$MODEL"; then
            echo "⚠️  Model $MODEL not found"
            echo "📥 Pulling model (this may take a while)..."
            ollama pull $MODEL
        else
            echo "✅ Model $MODEL is ready"
        fi
    fi
fi

echo ""
echo "🎨 Launching Streamlit Dashboard..."
echo "📍 Dashboard will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Launch Streamlit
streamlit run src/dashboard.py
