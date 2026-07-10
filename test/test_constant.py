"""
Tests for src.constant module - configuration constants and paths.
"""
import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestDirectoryPaths:
    """Test cases for directory path constants."""

    def test_base_dir_is_absolute(self):
        """Test that BASE_DIR is an absolute path."""
        from src.constant import BASE_DIR
        
        assert BASE_DIR.is_absolute()

    def test_appdata_dir_exists(self):
        """Test that APPDATA_DIR points to existing directory."""
        from src.constant import APPDATA_DIR
        
        assert APPDATA_DIR.exists()
        assert APPDATA_DIR.is_dir()

    def test_classes_dir_exists(self):
        """Test that CLASSES_DIR points to existing directory."""
        from src.constant import CLASSES_DIR
        
        assert CLASSES_DIR.exists()
        assert CLASSES_DIR.is_dir()

    def test_language_dir_exists(self):
        """Test that LANGUAGE_DIR points to existing directory."""
        from src.constant import LANGUAGE_DIR
        
        assert LANGUAGE_DIR.exists()
        assert LANGUAGE_DIR.is_dir()

    def test_style_dir_exists(self):
        """Test that STYLE_DIR points to existing directory."""
        from src.constant import STYLE_DIR
        
        assert STYLE_DIR.exists()
        assert STYLE_DIR.is_dir()

    def test_data_file_path_correct(self):
        """Test that DATA_FILE has correct path structure."""
        from src.constant import DATA_FILE, APPDATA_DIR
        
        assert DATA_FILE.parent == APPDATA_DIR
        assert DATA_FILE.name == 'data.json'


class TestWindowConstants:
    """Test cases for window-related constants."""

    def test_window_opacity_range(self):
        """Test that WINDOW_OPACITY is within valid range (0.0 to 1.0)."""
        from src.constant import WINDOW_OPACITY
        
        assert 0.0 <= WINDOW_OPACITY <= 1.0

    def test_window_dimensions_positive(self):
        """Test that window dimensions are positive integers."""
        from src.constant import ROOT_WINDOW_WIDTH, ROOT_WINDOW_HEIGHT
        
        assert ROOT_WINDOW_WIDTH > 0
        assert ROOT_WINDOW_HEIGHT > 0
        assert isinstance(ROOT_WINDOW_WIDTH, int)
        assert isinstance(ROOT_WINDOW_HEIGHT, int)

    def test_edge_hidden_delay_positive(self):
        """Test that EDGE_HIDDEN_DELAY_TIME is positive."""
        from src.constant import EDGE_HIDDEN_DELAY_TIME
        
        assert EDGE_HIDDEN_DELAY_TIME > 0

    def test_edge_pos_fault_tolerance_non_negative(self):
        """Test that EDGE_POS_FAULT_TOLERANCE is non-negative."""
        from src.constant import EDGE_POS_FAULT_TOLERANCE
        
        assert EDGE_POS_FAULT_TOLERANCE >= 0


class TestDebugMode:
    """Test cases for DEBUG mode detection."""

    def test_debug_is_boolean(self):
        """Test that DEBUG constant is a boolean."""
        from src.constant import DEBUG
        
        assert isinstance(DEBUG, bool)

    def test_debug_false_when_no_file(self):
        """Test that DEBUG is False when DEBUG file doesn't exist."""
        from src.constant import BASE_DIR
        
        debug_file = BASE_DIR / "DEBUG"
        # Ensure DEBUG file doesn't exist
        if debug_file.exists():
            debug_file.unlink()
        
        import importlib
        import src.constant
        importlib.reload(src.constant)
        
        assert src.constant.DEBUG is False

    def test_debug_true_when_file_exists(self, temp_dir):
        """Test that DEBUG is True when DEBUG file exists."""
        from src.constant import BASE_DIR
        
        debug_file = BASE_DIR / "DEBUG"
        debug_file.touch()
        
        try:
            import importlib
            import src.constant
            importlib.reload(src.constant)
            
            assert src.constant.DEBUG is True
        finally:
            # Clean up the DEBUG file
            if debug_file.exists():
                debug_file.unlink()


class TestModeConstants:
    """Test cases for animation mode identifiers."""

    def test_mode_hide_value(self):
        """Test MODE_HIDE constant value."""
        from src.constant import MODE_HIDE
        
        assert MODE_HIDE == 'hide'

    def test_mode_show_value(self):
        """Test MODE_SHOW constant value."""
        from src.constant import MODE_SHOW
        
        assert MODE_SHOW == 'show'

    def test_mode_constants_are_strings(self):
        """Test that mode constants are strings."""
        from src.constant import MODE_HIDE, MODE_SHOW
        
        assert isinstance(MODE_HIDE, str)
        assert isinstance(MODE_SHOW, str)


class TestPathRelationships:
    """Test relationships between different path constants."""

    def test_all_dirs_under_base_dir(self):
        """Test that all directories are under BASE_DIR."""
        from src.constant import (
            BASE_DIR, APPDATA_DIR, CLASSES_DIR, 
            LANGUAGE_DIR, STYLE_DIR
        )
        
        assert APPDATA_DIR.parent == BASE_DIR
        assert CLASSES_DIR.parent == BASE_DIR
        assert LANGUAGE_DIR.parent == APPDATA_DIR
        assert STYLE_DIR.parent == APPDATA_DIR

    def test_language_files_exist(self):
        """Test that language directory contains JSON files."""
        from src.constant import LANGUAGE_DIR
        
        json_files = list(LANGUAGE_DIR.glob('*.json'))
        assert len(json_files) > 0

    def test_style_files_exist(self):
        """Test that style directory contains CSS files."""
        from src.constant import STYLE_DIR
        
        css_files = list(STYLE_DIR.glob('*.css'))
        assert len(css_files) > 0

    def test_example_class_file_exists(self):
        """Test that example class file exists."""
        from src.constant import CLASSES_DIR
        
        example_file = CLASSES_DIR / 'example.csv'
        assert example_file.exists()
