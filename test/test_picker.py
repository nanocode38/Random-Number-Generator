"""
Tests for src.picker module - StudentPicker class functionality.
"""
import csv
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestStudentPickerInitialization:
    """Test cases for StudentPicker initialization."""

    def test_init_loads_class_names(self, temp_dir, mock_main_window, mock_language_data):
        """Test that StudentPicker loads available class files on initialization."""
        from src.picker import StudentPicker
        
        # Create test CSV files
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        (classes_dir / "class1.csv").write_text("A,B,C", encoding='utf-8')
        (classes_dir / "class2.csv").write_text("D,E,F", encoding='utf-8')
        (classes_dir / "not_csv.txt").write_text("ignore me", encoding='utf-8')
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            picker = StudentPicker(mock_main_window, mock_language_data, 'class1')
            
        assert 'class1' in picker.class_names
        assert 'class2' in picker.class_names
        assert 'not_csv' not in picker.class_names

    def test_init_sets_selected_class(self, temp_dir, mock_main_window, mock_language_data):
        """Test that StudentPicker correctly sets the selected class."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        (classes_dir / "myclass.csv").write_text("Student1,Student2", encoding='utf-8')
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            picker = StudentPicker(mock_main_window, mock_language_data, 'myclass')
            
        assert picker.selected_class == 'myclass'


class TestLoadNumNameList:
    """Test cases for load_num_name_list method."""

    def test_load_single_row_csv(self, temp_dir, mock_main_window, mock_language_data):
        """Test loading CSV with single row (names only, auto-generated numbers)."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        csv_file = classes_dir / "test.csv"
        csv_file.write_text("Alice,Bob,Charlie", encoding='utf-8')
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            picker = StudentPicker(mock_main_window, mock_language_data, 'test')
            
        assert picker._name_list == ['Alice', 'Bob', 'Charlie']
        assert picker._num_list == [1, 2, 3]

    def test_load_two_row_csv(self, temp_dir, mock_main_window, mock_language_data):
        """Test loading CSV with two rows (custom numbers and names)."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        csv_file = classes_dir / "test.csv"
        csv_file.write_text("101,102,103\nAlice,Bob,Charlie", encoding='utf-8')
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            picker = StudentPicker(mock_main_window, mock_language_data, 'test')
            
        assert picker._name_list == ['Alice', 'Bob', 'Charlie']
        assert picker._num_list == ['101', '102', '103']

    def test_load_nonexistent_file_shows_warning(self, temp_dir, mock_main_window, mock_language_data):
        """Test that loading non-existent file shows warning message."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
                picker = StudentPicker(mock_main_window, mock_language_data, 'nonexistent')
                
        mock_warning.assert_called_once()

    def test_load_invalid_format_shows_warning(self, temp_dir, mock_main_window, mock_language_data):
        """Test that loading invalid format file shows warning."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        csv_file = classes_dir / "invalid.csv"
        # Three rows - invalid format
        csv_file.write_text("Row1\nRow2\nRow3", encoding='utf-8')
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
                picker = StudentPicker(mock_main_window, mock_language_data, 'invalid')
                
        mock_warning.assert_called()


class TestOnClassChanged:
    """Test cases for on_class_changed method."""

    def test_on_class_changed_updates_selection(self, temp_dir, mock_main_window, mock_language_data):
        """Test that changing class updates selected_class and reloads data."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        (classes_dir / "class1.csv").write_text("A,B", encoding='utf-8')
        (classes_dir / "class2.csv").write_text("X,Y,Z", encoding='utf-8')
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            picker = StudentPicker(mock_main_window, mock_language_data, 'class1')
            initial_name_list = picker._name_list.copy()
            
            picker.on_class_changed('class2')
            
        assert picker.selected_class == 'class2'
        assert picker._name_list != initial_name_list
        assert picker._name_list == ['X', 'Y', 'Z']


class TestMakeRandom:
    """Test cases for make_random method."""

    def test_make_random_selects_student(self, temp_dir, mock_main_window, mock_language_data):
        """Test that make_random selects a student and updates labels."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        csv_file = classes_dir / "test.csv"
        csv_file.write_text("Alice,Bob,Charlie,David,Eve", encoding='utf-8')
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            picker = StudentPicker(mock_main_window, mock_language_data, 'test')
            picker.make_random()
            
        # Verify labels were updated
        mock_main_window.num_label.setText.assert_called_once()
        mock_main_window.name_label.setText.assert_called_once()
        
        # Verify the selected student is valid
        called_name = mock_main_window.name_label.setText.call_args[0][0]
        assert called_name in ['Alice', 'Bob', 'Charlie', 'David', 'Eve']

    def test_make_random_with_deduplication(self, temp_dir, mock_main_window, mock_language_data):
        """Test make_random with deduplication mode enabled."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        csv_file = classes_dir / "test.csv"
        csv_file.write_text("Alice,Bob", encoding='utf-8')
        
        mock_main_window.dedup_check.isChecked.return_value = True
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            picker = StudentPicker(mock_main_window, mock_language_data, 'test')
            
            # First selection
            picker.make_random()
            first_selection = mock_main_window.name_label.setText.call_args[0][0]
            
            # Second selection should be different (deduplication)
            picker.make_random()
            second_selection = mock_main_window.name_label.setText.call_args[0][0]
            
        # With only 2 students and deduplication, they should be different
        assert first_selection != second_selection

    def test_make_random_dedup_all_drawn_resets(self, temp_dir, mock_main_window, mock_language_data):
        """Test that deduplication resets when all students are drawn."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        csv_file = classes_dir / "test.csv"
        csv_file.write_text("Alice,Bob", encoding='utf-8')
        
        mock_main_window.dedup_check.isChecked.return_value = True
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            with patch('PySide6.QtWidgets.QMessageBox.information') as mock_info:
                picker = StudentPicker(mock_main_window, mock_language_data, 'test')
                
                # Draw all students
                picker.make_random()
                picker.make_random()
                
                # Next draw should trigger reset message
                picker.make_random()
                
        mock_info.assert_called_once()
        assert len(picker._drawn_indices) == 0  # Should be cleared

    def test_make_random_tracks_drawn_indices(self, temp_dir, mock_main_window, mock_language_data):
        """Test that make_random properly tracks drawn indices."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        csv_file = classes_dir / "test.csv"
        csv_file.write_text("A,B,C,D,E", encoding='utf-8')
        
        mock_main_window.dedup_check.isChecked.return_value = True
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            picker = StudentPicker(mock_main_window, mock_language_data, 'test')
            
            # Make several random selections
            for _ in range(3):
                picker.make_random()
                
        assert len(picker._drawn_indices) == 3


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_csv_file(self, temp_dir, mock_main_window, mock_language_data):
        """Test handling of empty CSV file."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        csv_file = classes_dir / "empty.csv"
        csv_file.write_text("", encoding='utf-8')
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            with patch('PySide6.QtWidgets.QMessageBox.warning'):
                picker = StudentPicker(mock_main_window, mock_language_data, 'empty')
                
        assert picker._name_list == []
        assert picker._num_list == []

    def test_mismatched_rows_in_two_row_csv(self, temp_dir, mock_main_window, mock_language_data):
        """Test handling of mismatched row lengths in two-row CSV."""
        from src.picker import StudentPicker
        
        classes_dir = temp_dir / "Classes"
        classes_dir.mkdir()
        csv_file = classes_dir / "mismatch.csv"
        csv_file.write_text("1,2,3\nAlice,Bob", encoding='utf-8')  # 3 numbers, 2 names
        
        with patch('src.picker.CLASSES_DIR', classes_dir):
            with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
                picker = StudentPicker(mock_main_window, mock_language_data, 'mismatch')
                
        mock_warning.assert_called()
