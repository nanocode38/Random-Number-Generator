from __future__ import annotations

import csv
import os
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ui import MainWindow

from PySide6.QtWidgets import QMessageBox

from .constant import CLASSES_DIR
from .logger import logger

class StudentPicker:
    """Handles random student selection from CSV class rosters,
    with optional deduplication support.
    """

    def __init__(self, main_window: MainWindow, language_data: dict, class_: str):
        logger.debug("Initializing StudentPicker (class=%s)", class_)
        self.main_window = main_window
        self.language_data = language_data
        self.selected_class = class_
        self.class_names: list[str] = []
        self._drawn_indices: set[int] = set()
        self._name_list, self._num_list = [], []

        # Load available class files
        logger.debug("Scanning for CSV class files in: %s", CLASSES_DIR)
        for file in os.listdir(CLASSES_DIR):
            if file.endswith('.csv'):
                self.class_names.append(file.replace('.csv', ''))
        logger.debug("Found %d class files: %s", len(self.class_names), self.class_names)

        self.load_num_name_list()

    def on_class_changed(self, text: str):
        logger.info("Class changed to: %s", text)
        self.selected_class = text
        self.load_num_name_list()

    def make_random(self):
        n = len(self._name_list)
        dedup = self.main_window.dedup_check.isChecked()
        logger.debug("Making random selection (total=%d, dedup=%s, drawn=%d)",
                      n, dedup, len(self._drawn_indices))

        if n == 0:
            logger.warning("No students available for random selection")
            return

        rand = random.randint(0, n - 1)
        while dedup:
            if rand not in self._drawn_indices:
                break
            if len(self._drawn_indices) == n:
                logger.info("All %d students have been drawn, resetting deduplication pool", n)
                QMessageBox.information(
                    self.main_window,
                    self.language_data["Title"],
                    self.language_data["Class file all drawn"],
                )
                self._drawn_indices.clear()
                return
            rand = random.randint(0, n - 1)

        self._drawn_indices.add(rand)
        num = self._num_list[rand]
        name = self._name_list[rand]
        logger.info("Random selection: index=%d, num=%s, name=%s", rand, num, name)
        self.main_window.num_label.setText(str(num))
        self.main_window.name_label.setText(name)

    def load_num_name_list(self):
        filepath = CLASSES_DIR / f'{self.selected_class}.csv'
        logger.debug("Loading class roster from: %s", filepath)
        if not os.path.exists(filepath):
            logger.warning("Class file not found: %s", filepath)
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
                logger.debug("Single-row CSV detected (names only, auto-generating numbers)")
                self._name_list = list(next(reader, None))
                self._num_list = list(range(1, len(self._name_list) + 1))
            elif lens == 2:
                logger.debug("Two-row CSV detected (custom numbers + names)")
                self._num_list = list(next(reader, None))
                self._name_list = list(next(reader, None))

            if len(self._name_list) != len(self._num_list) or lens not in (1, 2):
                logger.warning("Invalid CSV format in '%s' (rows=%d, names=%d, nums=%d)",
                               filepath, lens, len(self._name_list), len(self._num_list))
                QMessageBox.warning(
                    self.main_window,
                    self.language_data["Class file error title"],
                    self.language_data["Class file style error"],
                )
                return

        logger.debug("Class roster loaded: %d students", len(self._name_list))
