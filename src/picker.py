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

    def __init__(self, main_window: MainWindow, language_data: dict, class_: str):
        self.main_window = main_window
        self.language_data = language_data
        self.selected_class = class_
        self.class_names: list[str] = []
        self._drawn_indices: set[int] = set()
        self._name_list, self._num_list = [], []

        # Load available class files
        for file in os.listdir(CLASSES_DIR):
            if file.endswith('.csv'):
                self.class_names.append(file.replace('.csv', ''))

        self.load_num_name_list()

    def on_class_changed(self, text: str):
        self.selected_class = text
        self.load_num_name_list()

    def make_random(self):
        n = len(self._name_list)
        dedup = self.main_window.dedup_check.isChecked()
        rand = random.randint(0, n - 1)
        while dedup:
            if rand not in self._drawn_indices:
                break
            if len(self._drawn_indices) == n:
                QMessageBox.information(
                    self.main_window,
                    self.language_data["Title"],
                    self.language_data["Class file all drawn"],
                )
                self._drawn_indices.clear()
                return
            rand = random.randint(0, n - 1)

        self._drawn_indices.add(rand)
        self.main_window.num_label.setText(str(self._num_list[rand]))
        self.main_window.name_label.setText(self._name_list[rand])

    def load_num_name_list(self):
        filepath = CLASSES_DIR / f'{self.selected_class}.csv'
        if not os.path.exists(filepath):
            QMessageBox.warning(
                self.main_window,
                self.language_data["Class file error title"],
                f'{self.language_data["Class file not found"]} {filepath}',
            )
            return
        with open(filepath, newline='', encoding='utf-8') as f:
            f.seek(0)
            reader = csv.reader(f)
            lens = len(f.readlines())
            f.seek(0)
            if lens == 1:
                self._name_list = list(next(reader, None))
                self._num_list = list(range(1, len(self._name_list) + 1))
            elif lens == 2:
                self._num_list = list(next(reader, None))
                self._name_list = list(next(reader, None))

            if len(self._name_list) != len(self._num_list) or lens not in (1, 2):
                QMessageBox.warning(
                    self.main_window,
                    self.language_data["Class file error title"],
                    self.language_data["Class file style error"],
                )
