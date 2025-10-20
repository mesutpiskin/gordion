# Gordion AI Code Review Agent - AI Assistant Instructions

## Project Overview
Gordion is an autonomous AI agent for reviewing pull requests on Bitbucket Server/Stash. The agent analyzes code changes using either local Ollama models providing approval decisions and inline comments.

## Core Architecture

### Key Components
- `main.py` - Entry point and scheduler
- `ai_agent.py` - OpenAI integration for code analysis
- `ollama_agent.py` - Local AI model integration
- `pr_analyzer.py` - Core PR analysis logic
- `stash_client.py` - Bitbucket/Stash API client
- `dashboard.py` - Streamlit-based monitoring UI

### Data Flow
1. Scheduler polls Bitbucket for new PRs
2. PR Analyzer evaluates changes against size thresholds
3. AI Agent (OpenAI/Ollama) analyzes code and generates review
4. Results are stored and PR is updated via Stash client

## Development Workflows

### Local Setup
```bash
# Install dependencies and setup environment
./setup.sh
cp .env.example .env  # Configure STASH_URL + STASH_TOKEN

# Verify connection
python3 tests/test_connection.py

# Start agent
./agent.sh start
```

### Testing
- Run unit tests: `python -m pytest tests/`
- Key test files: `test_ai.py`, `test_auth.py`, `test_connection.py`

## Project Conventions

### Configuration
- Main config: `config/config.yaml`
- Repository-specific rules: `config/repository_rules.yaml` 
- Environment variables in `.env`

### Code Patterns
- Use Python logging with proper levels
- AI analysis results always in JSON format
- PR size limits configured in approval_criteria
- Repository rules for custom per-repo behavior

### Critical Integration Points
- Bitbucket Server API (REST v1)
- OpenAI API (GPT-4)
- Ollama API (Local models)
- SQLite for persistent storage

## Key Files to Review
- `config/config.yaml` - Core configuration
- `src/pr_analyzer.py` - PR evaluation logic
- `src/ai_agent.py` - AI integration patterns
- `src/main.py` - Application lifecycle
- `docs/` - Detailed documentation

## Testing Guidelines
- All new features require unit tests
- Use `test_connection.py` to verify setup
- Mock AI responses in tests using fixtures

## Common Workflows
1. Adding new AI models: Extend `ai_agent.py`/`ollama_agent.py`
2. Custom rules: Update `repository_rules.yaml`
3. Monitoring: Use dashboard at http://localhost:8501