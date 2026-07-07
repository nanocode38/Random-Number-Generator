"""
pytest configuration and shared fixtures for Random Student Number Generator tests.
"""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_language_data():
    """Provide mock language data for testing."""
    return {
        'Title': 'Test Title',
        'Class': 'Class',
        'Deduplication': 'Deduplication',
        'Hide': 'Hide Edge',
        'Button Text': 'Random',
        'About': 'About',
        'Help': 'Help',
        'Mode': 'Mode',
        'Language': 'Language',
        'Help Window Title': 'Help',
        'Help Text': 'This is help text',
        'About Text': 'About this application',
        'Restart Info': 'Restart required',
        'Language Error': 'Language error: {type} {e} {id}',
        'Class file error title': 'Class File Error',
        'Class file not found': 'Class file not found:',
        'Class file style error': 'Invalid class file format',
        'Class file all drawn': 'All students have been selected'
    }


@pytest.fixture
def sample_csv_single_row(temp_dir):
    """Create a sample CSV file with single row (names only)."""
    csv_file = temp_dir / "test_class.csv"
    csv_file.write_text("Alice,Bob,Charlie,David,Eve", encoding='utf-8')
    return csv_file


@pytest.fixture
def sample_csv_two_rows(temp_dir):
    """Create a sample CSV file with two rows (numbers and names)."""
    csv_file = temp_dir / "test_class.csv"
    csv_file.write_text("101,102,103,104,105\nAlice,Bob,Charlie,David,Eve", encoding='utf-8')
    return csv_file


@pytest.fixture
def sample_settings():
    """Provide sample settings dictionary."""
    return {
        'Deduplication mode': False,
        'Edge hiding mode': False,
        'Language': 'English',
        'Mode': 'Light',
        'Class': 'example'
    }


@pytest.fixture
def mock_main_window():
    """Create a mock MainWindow for testing without GUI."""
    window = MagicMock()
    window.dedup_check = MagicMock()
    window.dedup_check.isChecked.return_value = False
    window.num_label = MagicMock()
    window.name_label = MagicMock()
    window.class_combo = MagicMock()
    window.hide_check = MagicMock()
    window.random_btn = MagicMock()
    window.mode_menu = MagicMock()
    window.lang_menu = MagicMock()
    return window


@pytest.fixture
def mock_qapplication(monkeypatch):
    """Mock QApplication to avoid GUI initialization in tests."""
    mock_app = MagicMock()
    monkeypatch.setattr('PySide6.QtWidgets.QApplication.instance', lambda: mock_app)
    return mock_app
