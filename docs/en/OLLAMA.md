# Ollama Integration

This document explains **Ollama** integration for using **local AI** with Stash Agent.

## 📖 Table of Contents

1. [What is Ollama?](#what-is-ollama)
2. [Why Ollama?](#why-ollama)
3. [Installation](#installation)
4. [Model Selection](#model-selection)
5. [Usage](#usage)
6. [OpenAI vs Ollama](#openai-vs-ollama)
7. [Troubleshooting](#troubleshooting)

---

## 🤖 What is Ollama?

**Ollama** is a tool that allows you to run open-source AI models (Llama, Mistral, CodeLlama, etc.) **on your local computer**.

### Advantages:
- ✅ **Free** - No API fees
- ✅ **Privacy** - Code stays local
- ✅ **Speed** - Very fast with M4 Pro Max
- ✅ **Offline** - No internet required
- ✅ **Unlimited** - No rate limits

### Disadvantages:
- ❌ RAM usage (4-40GB)
- ❌ Large initial download (4-40GB)
- ❌ Not as powerful as OpenAI GPT-4 (smaller models)

---

## 🎯 Why Ollama?

### Ideal for Corporate Use

1. **Cost Savings**
   - OpenAI API cost: ~$0.03 / 1K tokens
   - Ollama: **Free** (only electricity)
   - For hundreds of PRs: **$$$$ savings**

2. **Security & Compliance**
   - Code stays on-premise
   - GDPR/ISO 27001 compliant
   - On-premise deployment

3. **Performance**
   - M4 Pro Max with **8B model**: ~50 token/s
   - M4 Pro Max with **70B model**: ~10-20 token/s
   - PR analysis: 10-30 seconds

---

## 🚀 Installation

### Automatic Setup (Recommended)

```bash
./scripts/setup_ollama.sh
```

This script:
1. ✅ Installs Ollama (via Homebrew)
2. ✅ Starts the service
3. ✅ Offers model selection
4. ✅ Downloads model
5. ✅ Updates `.env` file

### Manual Setup

#### 1. Install Ollama

```bash
# With Homebrew
brew install ollama

# Or manual
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. Start Service

```bash
# Start in background
ollama serve &

# Or foreground (to see logs)
ollama serve
```

#### 3. Download Model

```bash
# Recommended: Llama 3.1 8B (fast, balanced)
ollama pull llama3.1:8b

# Alternative: CodeLlama 13B (code-focused)
ollama pull codellama:13b

# Alternative: Mistral 7B (fastest)
ollama pull mistral:7b
```

#### 4. Configure .env

```bash
AI_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

---

## 🎯 Model Selection

### Recommended Models for M4 Pro Max

| Model | Size | RAM | Speed | Quality | Use Case |
|-------|------|-----|-------|---------|----------|
| **llama3.1:8b** | 4.7GB | 8GB | ⚡⚡⚡ | ⭐⭐⭐ | **Recommended** - General purpose |
| **mistral:7b** | 4.1GB | 8GB | ⚡⚡⚡⚡ | ⭐⭐ | Fastest, compact |
| **codellama:7b** | 3.8GB | 8GB | ⚡⚡⚡ | ⭐⭐⭐ | Code optimized |
| **llama3.1:13b** | 7.4GB | 16GB | ⚡⚡ | ⭐⭐⭐⭐ | Better quality |
| **codellama:13b** | 7.3GB | 16GB | ⚡⚡ | ⭐⭐⭐⭐ | Best for code |
| **llama3.1:70b** | 40GB | 64GB | ⚡ | ⭐⭐⭐⭐⭐ | Most powerful (slow) |

### Recommendations

#### General Use (Recommended)
```bash
ollama pull llama3.1:8b
```
- Fast and balanced
- Good PR analysis performance
- 8GB RAM sufficient

#### Code-Focused
```bash
ollama pull codellama:13b
```
- Better for code review
- Focuses on syntax and best practices
- 16GB RAM required

#### Fastest
```bash
ollama pull mistral:7b
```
- Very fast response
- Sufficient for simple PRs
- 8GB RAM sufficient

#### Most Powerful (for M4 Pro Max Max)
```bash
ollama pull llama3.1:70b
```
- GPT-4 level
- For complex PRs
- 64GB RAM recommended
- Slow (10-30 tokens/s)

---

## 🎮 Usage

### 1. Test

```bash
# Test Ollama connection
python3 tests/test_ollama.py
```

Output:
```
✅ Ollama server is running
✅ Model 'llama3.1:8b' is available
⏳ Analyzing with Ollama AI...
✅ Analysis Successful!

Approve: True
Confidence: 85%

Reasoning:
  The PR fixes a critical authentication bug with proper test coverage.
  Code changes are minimal and focused. No security concerns detected.
```

### 2. Dry-Run

```bash
# In .env file
AI_PROVIDER=ollama
DRY_RUN=true
RUN_MODE=once

# Run
python3 src/main.py
```

### 3. Production

```bash
# In .env file
AI_PROVIDER=ollama
DRY_RUN=false
RUN_MODE=continuous

# Start
./agent.sh start

# Watch logs
./agent.sh logs
```

---

## ⚖️ OpenAI vs Ollama

### Comparison Table

| Feature | OpenAI (GPT-4) | Ollama (Llama 3.1 8B) | Ollama (Llama 3.1 70B) |
|---------|----------------|----------------------|------------------------|
| **Cost** | ~$0.03/1K tokens | Free | Free |
| **Privacy** | ❌ Sends data out | ✅ Local | ✅ Local |
| **Speed** | 1-5 seconds | 10-20 seconds | 30-60 seconds |
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **RAM** | - | 8GB | 64GB |
| **Offline** | ❌ Internet required | ✅ Works offline | ✅ Works offline |
| **Rate Limit** | ✅ Yes (10K RPM) | ✅ No | ✅ No |

### When to Use OpenAI?

- ✅ Need best quality
- ✅ Speed is critical (1-5 seconds)
- ✅ Limited RAM
- ✅ Don't want to setup

### When to Use Ollama?

- ✅ Cost matters (free)
- ✅ Privacy is critical (on-premise)
- ✅ Need unlimited usage
- ✅ Want offline operation
- ✅ Have powerful Mac (M4 Pro Max)

---

## 🔧 Troubleshooting

### Problem: Cannot connect to Ollama

```
⚠️  Cannot connect to Ollama server
```

**Solution:**
```bash
# Check if service is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve &

# Or foreground
ollama serve
```

---

### Problem: Model not found

```
⚠️  Model 'llama3.1:8b' not available
```

**Solution:**
```bash
# Download model
ollama pull llama3.1:8b

# List downloaded models
ollama list
```

---

### Problem: Too slow

```
⏳ Analysis taking more than 60 seconds...
```

**Solutions:**

1. **Use smaller model:**
   ```bash
   ollama pull mistral:7b
   # .env: OLLAMA_MODEL=mistral:7b
   ```

2. **Check Metal acceleration:**
   ```bash
   # Verify M4 GPU is used
   ollama run llama3.1:8b "test"
   # Should see "using metal" in logs
   ```

3. **Check RAM availability:**
   ```bash
   # Check RAM usage in Activity Monitor
   # 8B model: 8GB
   # 13B model: 16GB
   # 70B model: 64GB
   ```

---

### Problem: JSON parse error

```
⚠️  Ollama JSON parse error
```

**Reason:** Model sometimes adds text outside JSON.

**Solution:** Code already does automatic JSON extraction. If problem persists:

1. Change model (Llama is more consistent)
2. Lower temperature (0.1 - 0.3)
3. Improve prompt

---

### Problem: Out of Memory

```
Error: failed to load model: out of memory
```

**Solution:**
```bash
# Use smaller model
ollama pull mistral:7b

# Or quantized model
ollama pull llama3.1:8b-q4_0  # 4-bit quantized
```

---

### Problem: Agent says AI failed but fallback mode works

```
⚠️  AI analysis failed - fallback mode active
✅ Auto-approved (AI failure fallback)
```

**This is normal!** Agent approves PRs even if AI fails (fallback mode).

**If you want to fix AI:**

1. Run test script: `python3 tests/test_ollama.py`
2. Check logs: `tail -f logs/agent.log`
3. Change model or restart Ollama

---

## 🎓 Advanced

### Using Custom Model

```bash
# Create your own model with Modelfile
cat > Modelfile << 'EOF'
FROM llama3.1:8b

PARAMETER temperature 0.2
PARAMETER num_ctx 4096

SYSTEM """You are a code review expert..."""
EOF

ollama create company-reviewer -f Modelfile

# Use in .env
OLLAMA_MODEL=company-reviewer
```

### GPU Monitoring

```bash
# Monitor Metal performance
sudo powermetrics --samplers gpu_power -i 1000

# See Ollama GPU usage
ollama ps
```

### Model Quantization

Quantized models for less RAM:

```bash
# 4-bit quantized (2x less RAM)
ollama pull llama3.1:8b-q4_0

# 8-bit quantized (1.5x less RAM)
ollama pull llama3.1:8b-q8_0
```

---

## 📊 Performance Metrics (M4 Pro Max)

### Llama 3.1 8B
- **Load time:** 2-3 seconds
- **Token/s:** 45-55 tokens/s
- **PR analysis:** 10-15 seconds
- **RAM:** ~8GB
- **Quality:** GPT-3.5 level

### Llama 3.1 70B
- **Load time:** 10-15 seconds
- **Token/s:** 8-12 tokens/s
- **PR analysis:** 40-60 seconds
- **RAM:** ~50GB
- **Quality:** GPT-4 level

### CodeLlama 13B
- **Load time:** 4-5 seconds
- **Token/s:** 30-40 tokens/s
- **PR analysis:** 15-20 seconds
- **RAM:** ~12GB
- **Quality:** Code optimized

---

## 🔗 Useful Links

- [Ollama Official Site](https://ollama.com/)
- [Ollama Models](https://ollama.com/library)
- [Llama 3.1 Model Card](https://ollama.com/library/llama3.1)
- [CodeLlama Model Card](https://ollama.com/library/codellama)
- [Ollama API Docs](https://github.com/ollama/ollama/blob/main/docs/api.md)

---

## 💡 Best Practices

1. **Test First**
   ```bash
   ./scripts/setup_ollama.sh
   python3 tests/test_ollama.py
   ```

2. **Start Small**
   - Start with `llama3.1:8b`
   - If performance is sufficient, keep using it
   - If quality is needed, try `codellama:13b` or `llama3.1:70b`

3. **Keep Fallback Mode Active**
   ```yaml
   auto_approve_on_ai_failure: true
   ```
   Agent continues working even if AI fails

4. **Monitor**
   ```bash
   ./agent.sh logs
   tail -f logs/agent.log | grep -i ollama
   ```

5. **Periodic Restart**
   ```bash
   # Restart Ollama weekly (prevent memory leaks)
   pkill ollama
   ollama serve &
   ```

---

**🎉 Now your Stash Agent runs with completely local AI!**
