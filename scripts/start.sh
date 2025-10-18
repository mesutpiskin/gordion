#!/bin/bash

# Quick Start Script for Stash Agent

set -e

# Get the parent directory (project root)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Change to project root directory
cd "$PROJECT_ROOT"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   🤖 Stash PR Auto-Approve Agent - Quick Start       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env dosyası bulunamadı!${NC}"
    echo ""
    echo "Lütfen önce .env dosyasını oluşturun:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    echo "Gerekli bilgiler:"
    echo "  - STASH_URL: https://stash.yourcompany.com.tr"
    echo "  - STASH_USERNAME: Kullanıcı adınız"
    echo "  - STASH_PASSWORD: Şifreniz (Personal Access Token değil!)"
    echo "  - OPENAI_API_KEY: OpenAI API key"
    exit 1
fi

echo -e "${GREEN}✓${NC} .env dosyası bulundu"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 bulunamadı!${NC}"
    echo "Lütfen Python 3.8 veya üstünü yükleyin"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $(python3 --version | cut -d' ' -f2) bulundu"

# Check dependencies
if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  Bağımlılıklar yüklü değil"
    echo "Yükleniyor..."
    pip3 install -q -r requirements.txt
    echo -e "${GREEN}✓${NC} Bağımlılıklar yüklendi"
else
    echo -e "${GREEN}✓${NC} Bağımlılıklar yüklü"
fi

# Create logs directory
mkdir -p logs
echo -e "${GREEN}✓${NC} Log dizini hazır"

echo ""
echo "─────────────────────────────────────────────────────────"
echo "  📋 Kurulum tamamlandı!"
echo "─────────────────────────────────────────────────────────"
echo ""
echo "Sonraki adımlar:"
echo ""
echo "1️⃣  Bağlantı testi:"
echo "   ${YELLOW}python3 tests/test_connection.py${NC}"
echo ""
echo "2️⃣  AI testi:"
echo "   ${YELLOW}python3 tests/test_ai.py${NC}"
echo ""
echo "3️⃣  Test modu (dry run):"
echo "   ${YELLOW}DRY_RUN=true python3 src/main.py${NC}"
echo ""
echo "4️⃣  Production başlat:"
echo "   ${YELLOW}./agent.sh start${NC}"
echo ""
echo "5️⃣  Logları izle:"
echo "   ${YELLOW}./agent.sh logs${NC}"
echo ""
echo "─────────────────────────────────────────────────────────"
echo ""
echo "🔍 Detaylı bilgi için:"
echo "   • README.md - Genel bilgi"
echo "   • docs/QUICKSTART.md - Hızlı başlangıç"
echo "   • docs/OVERVIEW.md - Genel bakış"
echo "   • docs/EXAMPLES.md - Kullanım örnekleri"
echo ""

# Ask if user wants to run tests
read -p "Bağlantı testini şimdi çalıştırmak ister misiniz? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Bağlantı testi çalıştırılıyor..."
    python3 tests/test_connection.py
fi

echo ""
echo "✨ Başarılar!"
echo ""
