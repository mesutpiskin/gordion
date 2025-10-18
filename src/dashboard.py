"""
Streamlit Dashboard for Stash PR Agent
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
import subprocess
import signal
import time
from pathlib import Path
import yaml
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from database import Database
from logger import setup_logger

# Page config
st.set_page_config(
    page_title="Gordion PR Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = Database()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .status-running {
        color: #28a745;
        font-weight: bold;
    }
    .status-stopped {
        color: #dc3545;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def load_config():
    """Load configuration from YAML"""
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def save_config(config):
    """Save configuration to YAML"""
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def check_agent_status():
    """Check if agent is running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "src/main.py"],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except:
        return False


def start_agent():
    """Start the agent in background"""
    try:
        subprocess.Popen(
            ["python3", "src/main.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=Path(__file__).parent.parent
        )
        db.add_agent_run("started", "Agent started from dashboard")
        return True
    except Exception as e:
        st.error(f"Failed to start agent: {e}")
        return False


def stop_agent():
    """Stop the agent"""
    try:
        result = subprocess.run(
            ["pkill", "-f", "src/main.py"],
            capture_output=True
        )
        db.add_agent_run("stopped", "Agent stopped from dashboard")
        return True
    except Exception as e:
        st.error(f"Failed to stop agent: {e}")
        return False


def get_log_tail(lines=100):
    """Get last N lines from log file"""
    log_file = Path(__file__).parent.parent / 'logs' / 'agent.log'
    if not log_file.exists():
        return "No logs available"
    
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            return ''.join(all_lines[-lines:])
    except Exception as e:
        return f"Error reading logs: {e}"


# Header
st.markdown('<h1 class="main-header">🤖 Gordion PR Agent Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Agent Control")
    
    is_running = check_agent_status()
    
    if is_running:
        st.markdown('<p class="status-running">● Running</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-stopped">○ Stopped</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Start" if not is_running else "↻ Restart"):
            if is_running:
                stop_agent()
                time.sleep(1)
            if start_agent():
                st.success("Agent started!")
                time.sleep(1)
                st.rerun()
    
    with col2:
        if st.button("⏹️ Stop", disabled=not is_running):
            if stop_agent():
                st.success("Agent stopped!")
                time.sleep(1)
                st.rerun()
    
    st.markdown("---")
    
    # Configuration
    st.header("🔧 Settings")
    
    config = load_config()
    
    # Load prompts config for language
    prompts_path = Path(__file__).parent.parent / 'config' / 'prompts.yaml'
    prompts_config = {}
    if prompts_path.exists():
        with open(prompts_path, 'r', encoding='utf-8') as f:
            prompts_config = yaml.safe_load(f)
    
    # Language selection
    current_language = prompts_config.get('language', 'tr')
    language = st.selectbox(
        "🌍 Language / Dil",
        ['tr', 'en'],
        index=['tr', 'en'].index(current_language) if current_language in ['tr', 'en'] else 0,
        format_func=lambda x: '🇹🇷 Türkçe' if x == 'tr' else '🇬🇧 English'
    )
    
    if language != current_language:
        prompts_config['language'] = language
        with open(prompts_path, 'w', encoding='utf-8') as f:
            yaml.dump(prompts_config, f, default_flow_style=False, allow_unicode=True)
        lang_name = '🇹🇷 Türkçe' if language == 'tr' else '🇬🇧 English'
        st.success(f"Language changed to {lang_name}")
        st.info("⚠️ Restart agent to apply language change")
    
    # Model selection
    ai_config = config.get('ai', {})
    current_model = ai_config.get('ollama_model', 'deepseek-coder:33b')
    
    model = st.selectbox(
        "AI Model",
        ['deepseek-coder:33b', 'deepseek-coder:6.7b', 'llama3.1:8b', 'codellama:13b'],
        index=['deepseek-coder:33b', 'deepseek-coder:6.7b', 'llama3.1:8b', 'codellama:13b'].index(current_model) 
              if current_model in ['deepseek-coder:33b', 'deepseek-coder:6.7b', 'llama3.1:8b', 'codellama:13b'] else 0
    )
    
    if model != current_model:
        ai_config['ollama_model'] = model
        config['ai'] = ai_config
        save_config(config)
        st.success(f"Model changed to {model}")
    
    # Check interval
    approval_criteria = config.get('approval_criteria', {})
    check_interval = st.number_input(
        "Check Interval (seconds)",
        min_value=60,
        max_value=3600,
        value=config.get('check_interval', 300),
        step=60
    )
    
    if check_interval != config.get('check_interval'):
        config['check_interval'] = check_interval
        save_config(config)
        st.success(f"Interval updated to {check_interval}s")
    
    # Confidence threshold
    min_confidence = st.slider(
        "Min Confidence Score",
        0, 100,
        approval_criteria.get('min_confidence_score', 70)
    )
    
    if min_confidence != approval_criteria.get('min_confidence_score'):
        approval_criteria['min_confidence_score'] = min_confidence
        config['approval_criteria'] = approval_criteria
        save_config(config)
        st.success(f"Confidence threshold: {min_confidence}%")
    
    st.markdown("---")
    
    # Quick actions
    st.header("🗑️ Actions")
    if st.button("Clear History"):
        if db.clear_history():
            st.success("History cleared!")
            st.rerun()

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📋 Recent PRs", "📈 Analytics", "📝 Logs"])

with tab1:
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    stats_today = db.get_stats(days=1)
    stats_week = db.get_stats(days=7)
    
    with col1:
        st.metric(
            "Today's PRs",
            stats_today.get('total', 0),
            delta=None
        )
    
    with col2:
        st.metric(
            "Approved",
            stats_today.get('approved', 0),
            delta=None,
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Rejected",
            stats_today.get('rejected', 0),
            delta=None,
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Avg Confidence",
            f"{stats_today.get('avg_confidence', 0)}%",
            delta=None
        )
    
    st.markdown("---")
    
    # Weekly overview
    st.subheader("📅 This Week")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total PRs", stats_week.get('total', 0))
        st.metric("Files Changed", stats_week.get('total_files', 0))
    
    with col2:
        st.metric("Lines Added", f"+{stats_week.get('total_additions', 0)}")
        st.metric("Lines Deleted", f"-{stats_week.get('total_deletions', 0)}")
    
    # Daily trend chart
    daily_stats = db.get_daily_stats(days=7)
    
    if daily_stats:
        df_daily = pd.DataFrame(daily_stats)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_daily['date'],
            y=df_daily['approved'],
            name='Approved',
            marker_color='green'
        ))
        fig.add_trace(go.Bar(
            x=df_daily['date'],
            y=df_daily['rejected'],
            name='Rejected',
            marker_color='red'
        ))
        
        fig.update_layout(
            title='Daily PR Trends (Last 7 Days)',
            xaxis_title='Date',
            yaxis_title='Count',
            barmode='stack',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📋 Recent Pull Requests")
    
    recent_prs = db.get_recent_prs(limit=50)
    
    if recent_prs:
        # Convert to DataFrame
        df = pd.DataFrame(recent_prs)
        
        # Format timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Select columns to display
        display_cols = ['pr_id', 'project_key', 'repo_slug', 'title', 'author', 
                       'status', 'confidence_score', 'files_changed', 'timestamp']
        
        # Add status emoji
        status_emoji = {
            'approved': '✅',
            'rejected': '❌',
            'needs_work': '⚠️'
        }
        df['status_display'] = df['status'].map(lambda x: f"{status_emoji.get(x, '○')} {x}")
        
        # Display table
        st.dataframe(
            df[['pr_id', 'project_key', 'repo_slug', 'title', 'author', 
                'status_display', 'confidence_score', 'files_changed', 'timestamp']],
            column_config={
                "pr_id": "PR ID",
                "project_key": "Project",
                "repo_slug": "Repository",
                "title": "Title",
                "author": "Author",
                "status_display": "Status",
                "confidence_score": st.column_config.ProgressColumn(
                    "Confidence",
                    format="%d%%",
                    min_value=0,
                    max_value=100,
                ),
                "files_changed": "Files",
                "timestamp": "Time"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Expandable details
        st.markdown("---")
        st.subheader("🔍 PR Details")
        
        selected_pr_id = st.selectbox(
            "Select PR to view details",
            df['pr_id'].tolist(),
            format_func=lambda x: f"#{x} - {df[df['pr_id']==x]['title'].iloc[0]}"
        )
        
        if selected_pr_id:
            pr_detail = df[df['pr_id'] == selected_pr_id].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Project:** {pr_detail['project_key']}/{pr_detail['repo_slug']}")
                st.write(f"**Author:** {pr_detail['author']}")
                st.write(f"**Status:** {pr_detail['status_display']}")
            
            with col2:
                st.write(f"**Confidence:** {pr_detail['confidence_score']}%")
                st.write(f"**Files Changed:** {pr_detail['files_changed']}")
                st.write(f"**Changes:** +{pr_detail['additions']} -{pr_detail['deletions']}")
            
            if pr_detail['reasoning']:
                st.write("**AI Reasoning:**")
                st.info(pr_detail['reasoning'])
            
            if pr_detail['concerns']:
                st.write("**Concerns:**")
                import json
                try:
                    concerns = json.loads(pr_detail['concerns'])
                    for concern in concerns:
                        st.warning(concern)
                except:
                    st.warning(pr_detail['concerns'])
    else:
        st.info("No PR history yet. The agent will log PRs as it processes them.")

with tab3:
    st.subheader("📈 Analytics")
    
    # Time range selector
    time_range = st.selectbox("Time Range", ["Last 7 Days", "Last 30 Days", "All Time"])
    
    days = 7 if time_range == "Last 7 Days" else 30 if time_range == "Last 30 Days" else 9999
    
    stats = db.get_stats(days=days)
    
    if stats.get('total', 0) > 0:
        # Approval rate pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(
                values=[stats['approved'], stats['rejected'], stats['needs_work']],
                names=['Approved', 'Rejected', 'Needs Work'],
                title='PR Status Distribution',
                color_discrete_map={
                    'Approved': 'green',
                    'Rejected': 'red',
                    'Needs Work': 'orange'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Stats summary
            st.metric("Total PRs Processed", stats['total'])
            st.metric("Approval Rate", f"{stats['approved']/stats['total']*100:.1f}%")
            st.metric("Average Confidence", f"{stats['avg_confidence']}%")
            
        # Daily trends
        daily_stats = db.get_daily_stats(days=days)
        
        if daily_stats:
            df_daily = pd.DataFrame(daily_stats)
            
            fig_line = px.line(
                df_daily,
                x='date',
                y=['approved', 'rejected'],
                title='Approval Trends Over Time',
                labels={'value': 'Count', 'variable': 'Status'}
            )
            st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info(f"No data available for {time_range.lower()}")

with tab4:
    st.subheader("📝 Live Logs")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        log_lines = st.slider("Number of log lines", 50, 500, 100, 50)
    
    with col2:
        if st.button("🔄 Refresh Logs"):
            st.rerun()
    
    logs = get_log_tail(lines=log_lines)
    
    st.code(logs, language="log")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh (every 5s)")
    
    if auto_refresh:
        time.sleep(5)
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🤖 Gordion PR Agent Dashboard | Built with Streamlit | 
        <a href='https://github.com/yourusername/stash-agent' target='_blank'>GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)
