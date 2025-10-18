#!/bin/bash

# Ollama Kurulum ve Test Script
# M4 Pro Max için optimize edilmiş

echo "============================================================"
echo "Ollama Setup for Stash Agent"
echo "============================================================"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama bulunamadı. Kuruluyor..."
    echo ""
    
    # Install Ollama
    echo "📦 Ollama kuruluyor (Homebrew ile)..."
    brew install ollama
    
    if [ $? -ne 0 ]; then
        echo "❌ Homebrew kurulumu başarısız. Manuel kurulum için:"
        echo "   curl -fsSL https://ollama.com/install.sh | sh"
        exit 1
    fi
    
    echo "✅ Ollama kuruldu!"
else
    echo "✅ Ollama zaten kurulu"
fi

echo ""
echo "============================================================"
echo "Ollama Servisi Başlatılıyor..."
echo "============================================================"
echo ""

# Start Ollama service in background
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!
echo "✅ Ollama servisi başlatıldı (PID: $OLLAMA_PID)"
echo "   Log: /tmp/ollama.log"

# Wait for Ollama to start
echo ""
echo "⏳ Ollama'nın başlaması bekleniyor..."
sleep 3

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama servisi çalışıyor!"
else
    echo "❌ Ollama servisi başlatılamadı"
    exit 1
fi

echo ""
echo "============================================================"
echo "Önerilen Modeller (M4 Pro Max için)"
echo "============================================================"
echo ""
echo "🚀 HIZLI MODELLER (Önerilen):"
echo "   • llama3.1:8b      - Hızlı, genel amaçlı (4GB RAM)"
echo "   • mistral:7b       - Çok hızlı, kompakt (4GB RAM)"
echo "   • codellama:7b     - Kod odaklı, hızlı (4GB RAM)"
echo ""
echo "💪 GÜÇLÜ MODELLER (Daha iyi kalite):"
echo "   • llama3.1:13b     - Dengeli performans (8GB RAM)"
echo "   • codellama:13b    - Kod için optimize (8GB RAM)"
echo ""
echo "🔥 EN GÜÇLÜ MODELLER (En iyi kalite, yavaş):"
echo "   • llama3.1:70b     - En iyi kalite (40GB RAM)"
echo "   • codellama:34b    - Kod için en iyi (20GB RAM)"
echo ""

# Ask which model to install
echo "============================================================"
echo "Hangi modeli kurmak istersiniz?"
echo "============================================================"
echo ""
echo "1) llama3.1:8b      (Önerilen - Hızlı, genel amaçlı)"
echo "2) codellama:13b    (Kod odaklı, daha güçlü)"
echo "3) mistral:7b       (En hızlı, kompakt)"
echo "4) llama3.1:70b     (En güçlü - çok RAM gerekir)"
echo "5) Manuel seçim"
echo ""
read -p "Seçiminiz (1-5) [1]: " choice
choice=${choice:-1}

case $choice in
    1)
        MODEL="llama3.1:8b"
        ;;
    2)
        MODEL="codellama:13b"
        ;;
    3)
        MODEL="mistral:7b"
        ;;
    4)
        MODEL="llama3.1:70b"
        ;;
    5)
        read -p "Model adı girin (örn: llama3.1:8b): " MODEL
        ;;
    *)
        MODEL="llama3.1:8b"
        ;;
esac

echo ""
echo "============================================================"
echo "Model İndiriliyor: $MODEL"
echo "============================================================"
echo ""
echo "⚠️  İlk indirme büyük olabilir (4-40GB arası)"
echo "⏳ Lütfen bekleyin..."
echo ""

ollama pull $MODEL

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Model başarıyla indirildi: $MODEL"
else
    echo ""
    echo "❌ Model indirme başarısız"
    exit 1
fi

echo ""
echo "============================================================"
echo "Kurulum Tamamlandı!"
echo "============================================================"
echo ""
echo "✅ Ollama servisi çalışıyor"
echo "✅ Model hazır: $MODEL"
echo ""
echo "📝 .env dosyasını güncellemeyi unutmayın:"
echo "   AI_PROVIDER=ollama"
echo "   OLLAMA_MODEL=$MODEL"
echo ""
echo "🧪 Test etmek için:"
echo "   python3 tests/test_ollama.py"
echo ""
echo "🚀 Agent'ı başlatmak için:"
echo "   python3 src/main.py"
echo ""

# Update .env file
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    echo "📝 .env dosyası güncelleniyor..."
    
    # Update AI_PROVIDER
    if grep -q "^AI_PROVIDER=" "$ENV_FILE"; then
        sed -i '' "s/^AI_PROVIDER=.*/AI_PROVIDER=ollama/" "$ENV_FILE"
    fi
    
    # Update OLLAMA_MODEL
    if grep -q "^OLLAMA_MODEL=" "$ENV_FILE"; then
        sed -i '' "s/^OLLAMA_MODEL=.*/OLLAMA_MODEL=$MODEL/" "$ENV_FILE"
    fi
    
    echo "✅ .env dosyası güncellendi"
fi

echo ""
echo "💡 İpucu: Ollama servisi arka planda çalışıyor."
echo "   Durdurmak için: pkill ollama"
echo "   Yeniden başlatmak için: ollama serve &"
echo ""
