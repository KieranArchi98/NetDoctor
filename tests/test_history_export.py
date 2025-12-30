import os
import pytest
import tempfile
import json
from pathlib import Path
from netdoctor.storage import history
from netdoctor.core import report
from netdoctor import config

@pytest.fixture
def temp_storage(monkeypatch):
    """Fixture to use a temporary directory for storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        monkeypatch.setattr(history, "get_app_data_dir", lambda: tmp_path)
        yield tmp_path

def test_save_load_sqlite(temp_storage, monkeypatch):
    """Test saving and loading a session using SQLite."""
    monkeypatch.setattr(config, "STORAGE_TYPE", "sqlite")
    
    session_id = "test_sq"
    meta = {"tool": "TestTool", "target": "127.0.0.1"}
    results = [{"port": 80, "state": "open"}]
    
    history.save_session(session_id, meta, results)
    
    # List sessions
    sessions = history.list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["id"] == session_id
    assert sessions[0]["tool"] == "TestTool"
    
    # Load session
    loaded = history.load_session(session_id)
    assert loaded is not None
    assert loaded["id"] == session_id
    assert loaded["meta"] == meta
    assert loaded["results"] == results

def test_save_load_json(temp_storage, monkeypatch):
    """Test saving and loading a session using JSON."""
    monkeypatch.setattr(config, "STORAGE_TYPE", "json")
    
    session_id = "test_js"
    meta = {"tool": "TestJSON", "target": "localhost"}
    results = [{"seq": 1, "rtt": 0.5}]
    
    history.save_session(session_id, meta, results)
    
    # List sessions
    sessions = history.list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["id"] == session_id
    
    # Load session
    loaded = history.load_session(session_id)
    assert loaded is not None
    assert loaded["id"] == session_id
    assert loaded["results"] == results

def test_export_csv():
    """Test CSV export logic."""
    session = {
        "results": [
            {"port": 80, "state": "open", "service": "http"},
            {"port": 443, "state": "open", "service": "https"}
        ]
    }
    csv_out = report.export_csv(session)
    assert "port,state,service" in csv_out
    assert "80,open,http" in csv_out
    assert "443,open,https" in csv_out

def test_export_json():
    """Test JSON export logic."""
    session = {"id": "123", "results": [1, 2, 3]}
    json_out = report.export_json(session)
    loaded = json.loads(json_out)
    assert loaded["id"] == "123"
    assert loaded["results"] == [1, 2, 3]
