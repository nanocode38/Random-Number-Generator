"""
Tests for src.tools module - settings management and utility functions.
"""
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestLoadSettings:
    """Test cases for load_settings function."""

    def test_load_settings_success(self, temp_dir, sample_settings):
        """Test successfully loading settings from a valid JSON file."""
        from src.tools import load_settings
        
        # Create a temporary data.json file
        data_file = temp_dir / "data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_settings, f)
        
        # Patch DATA_FILE constant
        with patch('src.tools.DATA_FILE', data_file):
            result = load_settings()
            
        assert result == sample_settings
        assert isinstance(result, dict)
        assert 'Deduplication mode' in result
        assert 'Language' in result

    def test_load_settings_file_not_found(self, temp_dir):
        """Test loading settings when file doesn't exist (should use defaults)."""
        from src.tools import load_settings, _DEFAULT_SETTINGS
        
        non_existent_file = temp_dir / "nonexistent.json"
        
        with patch('src.tools.DATA_FILE', non_existent_file):
            with patch('src.tools.write_settings') as mock_write:
                result = load_settings()
                
        assert result == _DEFAULT_SETTINGS
        mock_write.assert_called_once()

    def test_load_settings_invalid_json(self, temp_dir):
        """Test loading settings from corrupted JSON file."""
        from src.tools import load_settings, _DEFAULT_SETTINGS
        
        data_file = temp_dir / "data.json"
        data_file.write_text("{ invalid json }", encoding='utf-8')
        
        with patch('src.tools.DATA_FILE', data_file):
            with patch('src.tools.write_settings') as mock_write:
                result = load_settings()
                
        assert result == _DEFAULT_SETTINGS
        mock_write.assert_called_once()


class TestWriteSettings:
    """Test cases for write_settings function."""

    def test_write_settings_success(self, temp_dir):
        """Test successfully writing settings to file."""
        from src.tools import write_settings
        
        data_file = temp_dir / "data.json"
        
        with patch('src.tools.DATA_FILE', data_file):
            write_settings(
                is_deduplication_mode=True,
                is_edge_hiding_mode=False,
                mode='Dark',
                language='English',
                class_='test_class'
            )
        
        # Verify file was created and contains correct data
        assert data_file.exists()
        with open(data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        assert saved_data['Deduplication mode'] is True
        assert saved_data['Edge hiding mode'] is False
        assert saved_data['Mode'] == 'Dark'
        assert saved_data['Language'] == 'English'
        assert saved_data['Class'] == 'test_class'

    def test_write_settings_overwrites_existing(self, temp_dir):
        """Test that write_settings overwrites existing file."""
        from src.tools import write_settings
        
        data_file = temp_dir / "data.json"
        
        # Write initial settings
        with patch('src.tools.DATA_FILE', data_file):
            write_settings(False, False, 'Light', 'English', 'class1')
            
        # Overwrite with new settings
        with patch('src.tools.DATA_FILE', data_file):
            write_settings(True, True, 'Dark', '中文 (简体)', 'class2')
            
        with open(data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        assert saved_data['Deduplication mode'] is True
        assert saved_data['Mode'] == 'Dark'
        assert saved_data['Class'] == 'class2'


class TestLoadLanguage:
    """Test cases for load_language function."""

    def test_load_language_success(self, temp_dir):
        """Test successfully loading language file."""
        from src.tools import load_language
        
        # Create a mock language file
        lang_dir = temp_dir / "language"
        lang_dir.mkdir()
        lang_file = lang_dir / "TestLang.json"
        test_lang_data = {'Title': 'Test', 'Button Text': 'Click'}
        
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(test_lang_data, f)
        
        with patch('src.tools.LANGUAGE_DIR', lang_dir):
            result = load_language('TestLang')
            
        assert result == test_lang_data
        assert result['Title'] == 'Test'

    def test_load_language_file_not_found(self, temp_dir):
        """Test loading non-existent language file raises exception."""
        from src.tools import load_language
        
        lang_dir = temp_dir / "language"
        lang_dir.mkdir()
        
        with patch('src.tools.LANGUAGE_DIR', lang_dir):
            with pytest.raises(FileNotFoundError):
                load_language('NonExistent')


class TestRestart:
    """Test cases for restart function."""

    @patch('src.tools.subprocess.Popen')
    @patch('src.tools.QApplication.quit')
    def test_restart_windows(self, mock_quit, mock_popen, monkeypatch):
        """Test restart functionality on Windows platform."""
        from src.tools import restart
        
        monkeypatch.setattr('sys.executable', '/usr/bin/python')
        monkeypatch.setattr('sys.argv', ['script.py', '--arg1'])
        monkeypatch.setattr('platform.system', lambda: 'Windows')
        
        restart()
        
        mock_popen.assert_called_once()
        mock_quit.assert_called_once()

    @patch('src.tools.subprocess.Popen')
    @patch('src.tools.QApplication.quit')
    def test_restart_non_windows(self, mock_quit, mock_popen, monkeypatch):
        """Test restart functionality on non-Windows platform."""
        from src.tools import restart
        
        monkeypatch.setattr('sys.executable', '/usr/bin/python')
        monkeypatch.setattr('sys.argv', ['script.py'])
        monkeypatch.setattr('platform.system', lambda: 'Linux')
        
        restart()
        
        mock_popen.assert_called_once()
        mock_quit.assert_called_once()


class TestSigintHandler:
    """Test cases for sigint_handler function."""

    @patch('src.tools.QApplication.quit')
    def test_sigint_handler_calls_quit(self, mock_quit):
        """Test that SIGINT handler calls QApplication.quit()."""
        from src.tools import sigint_handler
        
        sigint_handler(None, None)
        
        mock_quit.assert_called_once()
