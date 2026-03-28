#!/usr/bin/env python3
"""Unit tests for bridge.py"""

import pytest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import sys
sys.path.insert(0, '.')

from bridge import (
    tmux_exists,
    tmux_send,
    tmux_send_enter,
    tmux_send_escape,
    get_recent_sessions,
    get_session_id,
    send_typing_loop,
    setup_bot_commands,
    telegram_api,
)


class TestTmuxExists:
    """Tests for tmux_exists() function"""
    
    @patch('bridge.subprocess.run')
    def test_tmux_exists_true(self, mock_run):
        """Test when tmux session exists"""
        mock_run.return_value.returncode = 0
        assert tmux_exists() == True
        mock_run.assert_called_once()
    
    @patch('bridge.subprocess.run')
    def test_tmux_exists_false(self, mock_run):
        """Test when tmux session does not exist"""
        mock_run.return_value.returncode = 1
        assert tmux_exists() == False


class TestTmuxSend:
    """Tests for tmux send functions"""
    
    @patch('bridge.subprocess.run')
    def test_tmux_send_literal(self, mock_run):
        """Test sending text with literal flag"""
        tmux_send("hello world", literal=True)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "tmux" in call_args
        assert "send-keys" in call_args
        assert "-l" in call_args
        assert "hello world" in call_args
    
    @patch('bridge.subprocess.run')
    def test_tmux_send_not_literal(self, mock_run):
        """Test sending text without literal flag"""
        tmux_send("hello world", literal=False)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "-l" not in call_args
    
    @patch('bridge.subprocess.run')
    def test_tmux_send_enter(self, mock_run):
        """Test sending Enter key"""
        tmux_send_enter()
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "Enter" in call_args
    
    @patch('bridge.subprocess.run')
    def test_tmux_send_escape(self, mock_run):
        """Test sending Escape key"""
        tmux_send_escape()
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "Escape" in call_args


class TestGetRecentSessions:
    """Tests for get_recent_sessions() function"""
    
    @patch('bridge.os.path.exists')
    @patch('bridge.open', new_callable=mock_open, read_data='')
    def test_get_recent_sessions_empty_file(self, mock_file, mock_exists):
        """Test with empty history file"""
        mock_exists.return_value = True
        assert get_recent_sessions() == []
    
    @patch('bridge.os.path.exists')
    def test_get_recent_sessions_missing_file(self, mock_exists):
        """Test with missing history file"""
        mock_exists.return_value = False
        assert get_recent_sessions() == []
    
    @patch('bridge.os.path.exists')
    @patch('bridge.open', new_callable=mock_open)
    def test_get_recent_sessions_valid_data(self, mock_file, mock_exists):
        """Test with valid JSONL data"""
        mock_exists.return_value = True
        
        # Create valid JSONL data
        data = [
            {"timestamp": 1000, "project": "/path1", "display": "Session 1"},
            {"timestamp": 2000, "project": "/path2", "display": "Session 2"},
            {"timestamp": 3000, "project": "/path3", "display": "Session 3"},
            {"timestamp": 4000, "project": "/path4", "display": "Session 4"},
            {"timestamp": 5000, "project": "/path5", "display": "Session 5"},
        ]
        jsonl_content = "\n".join(json.dumps(d) for d in data)
        mock_file.return_value.read.return_value = jsonl_content
        mock_file.return_value.__iter__ = lambda self: iter(self.read().splitlines())
        
        result = get_recent_sessions(limit=3)
        
        # Should return 3 most recent (sorted by timestamp descending)
        assert len(result) == 3
        assert result[0]["timestamp"] == 5000
        assert result[1]["timestamp"] == 4000
        assert result[2]["timestamp"] == 3000
    
    @patch('bridge.os.path.exists')
    @patch('bridge.open', new_callable=mock_open)
    def test_get_recent_sessions_invalid_json(self, mock_file, mock_exists):
        """Test with invalid JSON lines"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = "invalid json\nalso invalid"
        mock_file.return_value.__iter__ = lambda self: iter(self.read().splitlines())
        
        result = get_recent_sessions()
        assert result == []


class TestGetSessionId:
    """Tests for get_session_id() function"""
    
    @patch('bridge.Path.exists')
    @patch('bridge.Path.glob')
    def test_get_session_id_valid_path(self, mock_glob, mock_exists):
        """Test with valid project path"""
        mock_exists.return_value = True
        
        # Mock glob to return a path
        mock_path = MagicMock()
        mock_path.stem = "test-session-id"
        mock_path.stat.return_value.st_mtime = 1234567890
        mock_glob.return_value = [mock_path]
        
        result = get_session_id("/some/project/path")
        
        assert result == "test-session-id"
    
    @patch('bridge.Path.exists')
    def test_get_session_id_invalid_path(self, mock_exists):
        """Test with invalid project path"""
        mock_exists.return_value = False
        
        result = get_session_id("/nonexistent/path")
        
        assert result is None


class TestTelegramApi:
    """Tests for telegram_api() function"""
    
    @patch('bridge.urllib.request.Request')
    @patch('bridge.urllib.request.urlopen')
    def test_telegram_api_success(self, mock_urlopen, mock_request):
        """Test successful API call"""
        # Set BOT_TOKEN directly for this test
        import bridge
        original_token = bridge.BOT_TOKEN
        bridge.BOT_TOKEN = "test-token"
        
        try:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({"ok": True}).encode()
            mock_urlopen.return_value.__enter__ = lambda self: mock_response
            mock_urlopen.return_value.__exit__ = lambda self, *args: None
            
            result = bridge.telegram_api("getMe", {})
            
            assert result == {"ok": True}
        finally:
            bridge.BOT_TOKEN = original_token
    
    @patch('bridge.urllib.request.urlopen')
    def test_telegram_api_error(self, mock_urlopen):
        """Test API call with error"""
        mock_urlopen.side_effect = Exception("Network error")
        
        result = telegram_api("getMe", {})
        
        assert result is None
    
    def test_telegram_api_no_token(self):
        """Test API call without token"""
        result = telegram_api("getMe", {})
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
