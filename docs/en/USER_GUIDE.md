# 🎨 Stash PR Agent - User Guide

## 📋 Table of Contents
1. [Installation](#installation)
2. [Dashboard Usage](#dashboard-usage)
3. [Basic Operations](#basic-operations)
4. [Settings](#settings)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Installation

### 1. Requirements
- Python 3.8 or higher
- pip (Python package manager)
- Git
- Ollama (for AI model)

### 2. Download Project
```bash
git clone <repository-url>
cd stash-agent
```

### 3. Create Environment File
```bash
# Copy .env.example
cp .env.example .env

# Edit .env file
nano .env
```

**Required fields:**
```properties
STASH_URL=https://stash.yourcompany.com.tr
STASH_USERNAME=YOUR_USERNAME
STASH_PASSWORD=YOUR_PASSWORD
OLLAMA_MODEL=deepseek-coder:33b
```

### 4. Install Ollama
```bash
# For macOS
brew install ollama

# Start Ollama
ollama serve &

# Download AI model (downloads 15-20GB on first run)
ollama pull deepseek-coder:33b

# Or for a smaller/faster model:
ollama pull deepseek-coder:6.7b
```

### 5. Start Dashboard
```bash
./start_dashboard.sh
```

✅ Opens automatically in browser: `http://localhost:8501`

---

## 🎨 Dashboard Usage

### Main Screen

```
┌─────────────────────────────────────────┐
│   🤖 Gordion PR Agent Dashboard          │
├─────────────────────────────────────────┤
│                                         │
│  📊 Overview  📋 PRs  📈 Analytics     │
│                                         │
│  Today's PRs: 5                         │
│  Approved: 4    Rejected: 1            │
│                                         │
│  [Last 24 hours chart]                 │
└─────────────────────────────────────────┘
```

### Side Panel (Left Side)

#### ⚙️ Agent Control
- **● Running / ○ Stopped**: Agent status
- **▶️ Start**: Start the agent
- **⏹️ Stop**: Stop the agent
- **↻ Restart**: Restart the agent

#### 🔧 Settings
- **AI Model**: AI model to use
  - `deepseek-coder:33b` - Most powerful (slow)
  - `deepseek-coder:6.7b` - Balanced (recommended)
  - `llama3.1:8b` - Fast
  
- **Check Interval**: PR check frequency (seconds)
  - Default: 300s (5 minutes)
  - Minimum: 60s
  
- **Min Confidence Score**: Auto-approval threshold
  - AI rejects if score is below this
  - Default: 70%

#### 🗑️ Actions
- **Clear History**: Delete all PR history

---

## 📊 Tabs

### 1. 📊 Overview
**Daily Statistics:**
- Today's PRs: Number of PRs processed today
- Approved: Approved PRs
- Rejected: Rejected PRs
- Avg Confidence: Average confidence score

**Weekly Summary:**
- Total PRs: Total processed PRs
- Files Changed: Number of changed files
- Lines Added/Deleted: Added/deleted lines

**Chart:** Daily PR trend for last 7 days

### 2. 📋 Recent PRs
**Table View:**
- PR ID, Project, Repo
- Title, Author
- Status (✅ Approved, ❌ Rejected, ⚠️ Needs Work)
- Confidence score (progress bar)
- File count, Time

**Detail View:**
- Select a PR to see details
- Read AI reasoning (decision rationale)
- View concerns

### 3. 📈 Analytics
**Time Range Selection:**
- Last 7 Days
- Last 30 Days
- All Time

**Visualizations:**
- PR Status Distribution (Pie chart)
  - Approved/Rejected/Needs Work distribution
- Approval Trends (Line chart)
  - Approval trend over time
- Statistics:
  - Total PRs Processed
  - Approval Rate
  - Average Confidence

### 4. 📝 Logs
**Live Log Viewer:**
- Shows last N lines (50-500)
- 🔄 Refresh: Manual refresh
- Auto-refresh: Auto-refresh every 5 seconds

**Log Colors:**
- 🟢 INFO: Normal information
- 🟡 WARNING: Warning
- 🔴 ERROR: Error

---

## 🎮 Basic Operations

### Starting the Agent
1. Open dashboard: `./start_dashboard.sh`
2. Click **▶️ Start** button in left panel
3. Agent starts running in background
4. Status changes to: **● Running**

### Stopping the Agent
1. Click **⏹️ Stop** button in left panel
2. Agent stops
3. Status changes to: **○ Stopped**

### Changing Model
1. Go to **Settings** section in left panel
2. Select model from **AI Model** dropdown
3. Saves automatically
4. Restart agent: **↻ Restart**

### Viewing PR History
1. Go to **📋 Recent PRs** tab
2. View all PRs in the table
3. Select a PR to view details

### Viewing Statistics
1. Go to **📈 Analytics** tab
2. Select time range
3. Review charts and metrics

### Following Logs
1. Go to **📝 Logs** tab
2. Check **Auto-refresh** checkbox
3. Watch real-time log stream

---

## ⚙️ Settings

### config/config.yaml

```yaml
# Check interval (seconds)
check_interval: 300

# PR Approval Criteria
approval_criteria:
  min_confidence_score: 70        # AI confidence score (0-100)
  max_files_changed: 50           # Max number of files
  max_lines_changed: 1000         # Max line changes
  
  auto_approve_on_ai_failure: true    # Approve if AI fails
  auto_approve_oversized: true        # Approve oversized PRs
  
  comment_on_reject: true             # Add comment on reject
  mark_needs_work_on_reject: true     # Mark as "Needs Work"
  decline_on_reject: false            # Decline PR (risky!)
  add_inline_comments_on_reject: true # Add line-by-line comments

# AI Model
ai:
  ollama_model: "deepseek-coder:33b"
  temperature: 0.3
  max_tokens: 2000
```

### .env File

```properties
# Stash credentials
STASH_URL=https://stash.yourcompany.com.tr
STASH_USERNAME=USERNAME
STASH_PASSWORD=PASSWORD

# Ollama settings
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:33b

# Agent settings
CHECK_INTERVAL=300
DRY_RUN=false
RUN_MODE=continuous
```

---

## 🔧 Troubleshooting

### Dashboard Not Opening
```bash
# Reinstall packages
pip install -r requirements.txt

# Start dashboard manually
streamlit run src/dashboard.py
```

### Cannot Connect to Ollama
```bash
# Check if Ollama is running
pgrep ollama

# Start if not running
ollama serve &

# Check model
ollama list

# Download if missing
ollama pull deepseek-coder:33b
```

### Agent Not Starting
1. Go to **Logs** tab
2. Read error messages
3. Common issues:
   - Missing/incorrect `.env` file
   - Ollama not running
   - Model not downloaded
   - Stash connection error

### Cannot Connect to Stash
```bash
# Check .env file
cat .env | grep STASH

# Test Stash URL
curl -u USERNAME:PASSWORD https://stash.yourcompany.com.tr/rest/api/1.0/users
```

### Model Too Slow
1. Use a smaller model:
   ```
   OLLAMA_MODEL=deepseek-coder:6.7b
   ```

2. Or:
   ```
   OLLAMA_MODEL=llama3.1:8b
   ```

### Database Errors
```bash
# Reset database
rm data/pr_history.db

# Restart dashboard
./start_dashboard.sh
```

---

## 💡 Tips

### Performance
- **deepseek-coder:33b**: Best analysis, slow (16GB RAM)
- **deepseek-coder:6.7b**: Balanced (8GB RAM)
- **llama3.1:8b**: Fast, general purpose (4GB RAM)

### Security
- **Never** commit `.env` file
- Prefer token over password
- Test first with `DRY_RUN=true`

### Usage
- Start with `min_confidence_score: 80`
- Monitor results, adjust if needed
- Keep `comment_on_reject: true` active
- Leave `decline_on_reject: false` (risky)

---

## 🆘 Support

Having issues?
1. Check **Logs** tab
2. Open an issue on GitHub
3. Contact your team lead

---

## 📚 More Information

- [README.md](../README.md) - General information
- [QUICKSTART.md](QUICKSTART.md) - Quick start
- [AUTHENTICATION.md](AUTHENTICATION.md) - Authentication
- [OLLAMA.md](OLLAMA.md) - Ollama setup
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration settings
- [DASHBOARD.md](DASHBOARD.md) - Dashboard features
- [MULTI_LANGUAGE.md](MULTI_LANGUAGE.md) - Language support

---

**🎉 Happy coding!**
