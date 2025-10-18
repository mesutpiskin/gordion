# Quick Start Guide

## 1. Installation

```bash
cd /Users/YOURUSER/Desktop/stash-agent
./setup.sh
```

## 2. Configuration

### Edit .env File

```bash
nano .env
```

Replace the following values with your own information:

```env
STASH_URL=https://stash.yourcompany.com.tr
STASH_USERNAME=your_username
STASH_PASSWORD=your_password
OPENAI_API_KEY=your_openai_api_key
```

### Authentication

**Important Note:** YourCompany Stash (legacy Bitbucket Server version) does not support Personal Access Tokens. Therefore, **Basic Authentication** (username + password) is used.

- `STASH_USERNAME`: Your Stash username
- `STASH_PASSWORD`: Your Stash password

**Security Note:** 
- Store your password in the `.env` file
- `.env` file is never committed to git (listed in `.gitignore`)
- On production servers, restrict file permissions with `chmod 600 .env`

## 3. Testing

### Connection Test
```bash
python3 tests/test_connection.py
```

If successful, it confirms you can connect to Stash and see assigned PRs.

### AI Agent Test
```bash
python3 tests/test_ai.py
```

Verifies that the OpenAI API is working.

## 4. Running

### Foreground (For Testing)
```bash
python3 src/main.py
```

Stop with CTRL+C.

### Background (Production)

#### Method 1: Using agent.sh script
```bash
# Start
./agent.sh start

# Check status
./agent.sh status

# Watch logs
./agent.sh logs

# Stop
./agent.sh stop

# Restart
./agent.sh restart
```

#### Method 2: Using nohup
```bash
nohup python3 src/main.py > logs/agent.log 2>&1 &
echo $! > logs/agent.pid
```

To stop:
```bash
kill $(cat logs/agent.pid)
```

#### Method 3: Using screen
```bash
screen -S stash-agent
python3 src/main.py

# Detach with CTRL+A+D
# Reattach with: screen -r stash-agent
```

#### Method 4: Using systemd (Linux)
```bash
sudo cp stash-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable stash-agent
sudo systemctl start stash-agent
sudo systemctl status stash-agent
```

#### Method 5: Using launchd (macOS)
```bash
cp com.company.stash-agent.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.company.stash-agent.plist
launchctl start com.company.stash-agent
```

## 5. Dashboard

### Start Dashboard
```bash
./start_dashboard.sh
```

Dashboard will open at: `http://localhost:8501`

**Features:**
- 📊 Real-time statistics
- 📋 PR history
- 📈 Analytics and charts
- 🤖 Agent control (start/stop)
- 🔧 Settings
- 📜 Live logs

## 6. Log Monitoring

### Real-time Logs
```bash
tail -f logs/agent.log
```

### Log Files
- `logs/agent.log` - Main agent logs
- `logs/dashboard.log` - Dashboard logs
- `logs/stash-agent-*.log` - Dated log files

## 7. What Agent Does

1. **Periodic Check**: Checks assigned PRs every 5 minutes
2. **Fetch Changes**: Downloads PR diffs (changed files + code)
3. **AI Analysis**: Analyzes code with Ollama/OpenAI
4. **Scoring**: Calculates confidence score (0-100)
5. **Action**:
   - ✅ **≥70 score**: Approves + adds positive comment
   - ❌ **<70 score**: Marks as "Needs Work" + adds detailed feedback
   - 💬 **Inline Comments**: Adds line-specific comments for issues

## 8. Common Commands

```bash
# Check agent status
ps aux | grep "python3 src/main.py"

# View logs
tail -f logs/agent.log

# Stop agent
pkill -f "python3 src/main.py"

# Start agent in background
nohup python3 src/main.py > logs/agent.log 2>&1 &

# Start dashboard
./start_dashboard.sh

# Run tests
python3 tests/test_connection.py
python3 tests/test_ai.py
```

## 9. Next Steps

- 📖 [User Guide](USER_GUIDE.md) - Detailed usage
- ⚙️ [Configuration](CONFIGURATION.md) - All settings
- 🤖 [Ollama Setup](OLLAMA.md) - AI model configuration
- 🔐 [Authentication](AUTHENTICATION.md) - Auth methods
- 📊 [Dashboard](DASHBOARD.md) - Web interface
- 🌍 [Multi-Language](MULTI_LANGUAGE.md) - Language support

## 10. Troubleshooting

### Agent Not Starting
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check dependencies
pip3 list | grep -E "requests|pyyaml|openai"

# Reinstall
./setup.sh
```

### Connection Errors
```bash
# Test connection
curl -u "username:password" "https://stash.yourcompany.com.tr/rest/api/1.0/inbox/pull-requests"

# Check .env file
cat .env | grep STASH
```

### AI Not Working
```bash
# Check Ollama
ollama list
ollama ps

# Test model
ollama run deepseek-coder:33b "test"

# Restart Ollama
pkill ollama
ollama serve &
```

### Dashboard Not Opening
```bash
# Check if port is in use
lsof -ti:8501

# Kill process
kill $(lsof -ti:8501)

# Restart dashboard
./start_dashboard.sh
```

## 11. Support

- 📧 Email: support@yourcompany.com
- 💬 Slack: #stash-agent-support
- 📝 Issues: Create an issue in the repository

---

**Happy Coding! 🚀**
