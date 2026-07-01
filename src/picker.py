from __future__ import annotations

import csv
import os
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ui import MainWindow

from PySide6.QtWidgets import QMessageBox

from .constant import CLASSES_DIR


class StudentPicker:
    """Handles random student selection from CSV class rosters,
    with optional deduplication support.
    """

    def __init__(self, main_window: MainWindow, language_data: dict):
        self.main_window = main_window
        self.language_data = language_data
        self.selected_class = ''
        self.class_names: list[str] = []
        self._drawn_indices: set[int] = set()

        # Load available class files
        for file in os.listdir(CLASSES_DIR):
            if file.endswith('.csv'):
                self.class_names.append(file.replace('.csv', ''))

    def on_class_changed(self, text: str):
        self.selected_class = text

    def make_random(self):
        cls = self.selected_class or 'example'
        filepath = CLASSES_DIR / f'{cls}.csv'
        if not os.path.exists(filepath):
            QMessageBox.warning(
                self.main_window,
                self.language_data["Class file error title"],
                f'{self.language_data["Class file error"]} {filepath}',
            )
            return
        with open(filepath, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        if not rows:
            return
        names = rows[0]  # Assume there is only one line of names
        n = len(names)

        if self.main_window.dedup_check.isChecked():
            # If everyone has been drawn
            if len(self._drawn_indices) >= n:
                QMessageBox.information(
                    self.main_window,
                    self.language_data['Title'],
                    self.language_data['Message'],
                )
                self._drawn_indices.clear()
                return
            idx = random.randint(0, n - 1)
            while idx in self._drawn_indices:
                idx = random.randint(0, n - 1)
        else:
            idx = random.randint(0, n - 1)

        self._drawn_indices.add(idx)
        self.main_window.num_label.setText(str(idx + 1))
        self.main_window.name_label.setText(names[idx])
