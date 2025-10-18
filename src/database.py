"""
Database module for storing PR history and statistics
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """Simple SQLite database for PR history"""
    
    def __init__(self, db_path: str = "data/pr_history.db"):
        """Initialize database connection"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pr_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pr_id INTEGER NOT NULL,
                    project_key TEXT NOT NULL,
                    repo_slug TEXT NOT NULL,
                    title TEXT,
                    author TEXT,
                    status TEXT NOT NULL,
                    confidence_score INTEGER,
                    reasoning TEXT,
                    concerns TEXT,
                    files_changed INTEGER,
                    additions INTEGER,
                    deletions INTEGER,
                    ai_model TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(project_key, repo_slug, pr_id, timestamp)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_pr_record(self, pr_data: Dict) -> bool:
        """
        Add a PR record to history
        
        Args:
            pr_data: Dictionary containing PR information
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO pr_history (
                        pr_id, project_key, repo_slug, title, author,
                        status, confidence_score, reasoning, concerns,
                        files_changed, additions, deletions, ai_model
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pr_data.get('pr_id'),
                    pr_data.get('project_key'),
                    pr_data.get('repo_slug'),
                    pr_data.get('title'),
                    pr_data.get('author'),
                    pr_data.get('status'),
                    pr_data.get('confidence_score'),
                    pr_data.get('reasoning'),
                    json.dumps(pr_data.get('concerns', [])),
                    pr_data.get('files_changed'),
                    pr_data.get('additions'),
                    pr_data.get('deletions'),
                    pr_data.get('ai_model')
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"PR record already exists: {pr_data.get('pr_id')}")
            return False
        except Exception as e:
            logger.error(f"Error adding PR record: {e}")
            return False
    
    def get_recent_prs(self, limit: int = 50) -> List[Dict]:
        """
        Get recent PR records
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of PR records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM pr_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching recent PRs: {e}")
            return []
    
    def get_stats(self, days: int = 7) -> Dict:
        """
        Get statistics for the last N days
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                        SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                        SUM(CASE WHEN status = 'needs_work' THEN 1 ELSE 0 END) as needs_work,
                        AVG(confidence_score) as avg_confidence,
                        SUM(files_changed) as total_files,
                        SUM(additions) as total_additions,
                        SUM(deletions) as total_deletions
                    FROM pr_history
                    WHERE timestamp >= datetime('now', '-' || ? || ' days')
                """, (days,))
                
                row = cursor.fetchone()
                
                return {
                    'total': row[0] or 0,
                    'approved': row[1] or 0,
                    'rejected': row[2] or 0,
                    'needs_work': row[3] or 0,
                    'avg_confidence': round(row[4] or 0, 1),
                    'total_files': row[5] or 0,
                    'total_additions': row[6] or 0,
                    'total_deletions': row[7] or 0
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """
        Get daily statistics for charts
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of daily statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                        SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
                    FROM pr_history
                    WHERE timestamp >= datetime('now', '-' || ? || ' days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """, (days,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return []
    
    def add_agent_run(self, status: str, message: str = "") -> bool:
        """
        Log an agent run
        
        Args:
            status: Run status (started, stopped, error)
            message: Optional message
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO agent_runs (status, message)
                    VALUES (?, ?)
                """, (status, message))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging agent run: {e}")
            return False
    
    def clear_history(self) -> bool:
        """Clear all PR history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM pr_history")
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False
