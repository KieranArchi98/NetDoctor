"""
History storage module for saving and loading diagnostic sessions.
"""

import os
import json
import sqlite3
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from netdoctor.config import STORAGE_TYPE, DB_FILENAME, JSON_HISTORY_FILENAME

def get_app_data_dir() -> Path:
    """Get the application data directory."""
    if os.name == 'nt':
        app_data = Path(os.getenv('APPDATA', os.path.expanduser('~'))) / 'NetDoctor'
    else:
        app_data = Path.home() / '.netdoctor'
    
    app_data.mkdir(parents=True, exist_ok=True)
    return app_data

def _get_sqlite_conn():
    """Get a connection to the SQLite database."""
    db_path = get_app_data_dir() / DB_FILENAME
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Create table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            tool TEXT,
            target TEXT,
            meta TEXT,
            results TEXT
        )
    ''')
    conn.commit()
    return conn

def save_session(session_id: str, meta: Dict[str, Any], results: List[Any]):
    """
    Save a diagnostic session.
    
    Args:
        session_id: Unique identifier for the session
        meta: Metadata dictionary (tool, target, etc.)
        results: List of result items
    """
    if STORAGE_TYPE == "sqlite":
        _save_sqlite(session_id, meta, results)
    else:
        _save_json(session_id, meta, results)

def _save_sqlite(session_id: str, meta: Dict[str, Any], results: List[Any]):
    conn = _get_sqlite_conn()
    tool = meta.get("tool", "unknown")
    target = meta.get("target", "unknown")
    
    # Convert meta and results to JSON strings
    meta_json = json.dumps(meta)
    results_json = json.dumps(results)
    
    conn.execute(
        "INSERT OR REPLACE INTO sessions (id, tool, target, meta, results) VALUES (?, ?, ?, ?, ?)",
        (session_id, tool, target, meta_json, results_json)
    )
    conn.commit()
    conn.close()

def _save_json(session_id: str, meta: Dict[str, Any], results: List[Any]):
    history_path = get_app_data_dir() / JSON_HISTORY_FILENAME
    history = {}
    
    if history_path.exists():
        try:
            with open(history_path, 'r') as f:
                history = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
            
    history[session_id] = {
        "id": session_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "tool": meta.get("tool", "unknown"),
        "target": meta.get("target", "unknown"),
        "meta": meta,
        "results": results
    }
    
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=4)

def list_sessions() -> List[Dict[str, Any]]:
    """List all saved sessions."""
    if STORAGE_TYPE == "sqlite":
        return _list_sqlite()
    else:
        return _list_json()

def _list_sqlite() -> List[Dict[str, Any]]:
    conn = _get_sqlite_conn()
    cursor = conn.execute("SELECT id, timestamp, tool, target FROM sessions ORDER BY timestamp DESC")
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions

def _list_json() -> List[Dict[str, Any]]:
    history_path = get_app_data_dir() / JSON_HISTORY_FILENAME
    if not history_path.exists():
        return []
        
    try:
        with open(history_path, 'r') as f:
            history = json.load(f)
            return [
                {
                    "id": s["id"],
                    "timestamp": s["timestamp"],
                    "tool": s["tool"],
                    "target": s["target"]
                }
                for s in history.values()
            ]
    except (json.JSONDecodeError, OSError):
        return []

def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Load a specific session's data."""
    if STORAGE_TYPE == "sqlite":
        return _load_sqlite(session_id)
    else:
        return _load_json(session_id)

def _load_sqlite(session_id: str) -> Optional[Dict[str, Any]]:
    conn = _get_sqlite_conn()
    cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        session = dict(row)
        session["meta"] = json.loads(session["meta"])
        session["results"] = json.loads(session["results"])
        return session
    return None

def _load_json(session_id: str) -> Optional[Dict[str, Any]]:
    history_path = get_app_data_dir() / JSON_HISTORY_FILENAME
    if not history_path.exists():
        return None
        
    try:
        with open(history_path, 'r') as f:
            history = json.load(f)
            return history.get(session_id)
    except (json.JSONDecodeError, OSError):
        return None
