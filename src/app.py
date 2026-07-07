import signal
import sys
import json
import os

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from .constant import (
    DEBUG,
    LANGUAGE_DIR,
    STYLE_DIR
)
from .tools import restart, sigint_handler, load_settings, write_settings, load_language
from .ui import MainWindow
from .edge_hider import EdgeHider
from .picker import StudentPicker

__version__ = '1.1.0'
__author__ = 'nanocode38'


class Main:
    """Lightweight coordinator that wires together the main window,
    student picker, and edge hider.
    """

    def __init__(self, is_deduplication_mode, is_edge_hiding_mode, mode, language, class_):
        self.current_mode = mode
        self.current_language = language
        self.language_data = load_language(language)

        # Create main window
        self.main_window = MainWindow(self.language_data, mode)
        self.main_window.apply_theme(mode)

        # Create components
        self.picker = StudentPicker(self.main_window, self.language_data, class_)
        self.edge_hider = EdgeHider(self.main_window)

        # Wire up widgets
        self._set_widgets_state(is_deduplication_mode, is_edge_hiding_mode)

        # Enable edge hiding if configured
        if is_edge_hiding_mode:
            self.edge_hider.enable()

        # Debug: allow Ctrl+C to interrupt
        if DEBUG:
            signal.signal(signal.SIGINT, sigint_handler)
            timer = QTimer()
            timer.start(500)
            timer.timeout.connect(lambda: None)

        self.main_window.show()
        QApplication.instance().aboutToQuit.connect(self.save_settings)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def save_settings(self):
        write_settings(
            self.main_window.dedup_check.isChecked(),
            self.main_window.hide_check.isChecked(),
            self.current_mode,
            self.current_language,
            self.picker.selected_class
        )

    # ------------------------------------------------------------------
    # Language switching
    # ------------------------------------------------------------------

    def change_language(self, language):
        try:
            language_file = LANGUAGE_DIR / f'{language}.json'
            with open(language_file, encoding='utf-8') as fp:
                self.language_data = json.load(fp)
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                self.language_data['Title'],
                self.language_data['Language Error'].format(
                    type=type(e).__name__, e=e, id=hex(id(e))
                ),
            )
            raise
        else:
            self.current_language = language
            if (
                QMessageBox.question(
                    self.main_window,
                    self.language_data['Title'],
                    self.language_data['Restart Info'],
                )
                == QMessageBox.Yes
            ):
                self.save_settings()
                restart()

    # ------------------------------------------------------------------
    # Edge-hiding toggle
    # ------------------------------------------------------------------

    def on_hide_mode_changed(self, state):
        is_edge_hiding = Qt.CheckState(state) == Qt.Checked
        if is_edge_hiding:
            self.edge_hider.enable()
        else:
            self.edge_hider.disable()

    # ------------------------------------------------------------------
    # Widget wiring
    # ------------------------------------------------------------------

    def _set_widgets_state(self, is_deduplication_mode, is_edge_hiding_mode):
        # Class combo
        self.main_window.class_combo.addItems(self.picker.class_names)
        self.main_window.class_combo.currentTextChanged.connect(self.picker.on_class_changed)

        # Checkboxes
        self.main_window.dedup_check.setChecked(is_deduplication_mode)
        self.main_window.hide_check.setChecked(is_edge_hiding_mode)
        self.main_window.hide_check.stateChanged.connect(self.on_hide_mode_changed)

        # Random button
        self.main_window.random_btn.clicked.connect(self.picker.make_random)

        # Mode menu
        for mode in STYLE_DIR.iterdir():
            if not mode.name.endswith('.css'):
                continue
            mode = mode.stem
            action = QAction(mode, self.main_window, checkable=False)
            action.triggered.connect(lambda checked, m=mode: self.main_window.change_mode(m))
            self.main_window.mode_menu.addAction(action)

        # Language menu
        for lang_file in os.listdir(LANGUAGE_DIR):
            if lang_file.endswith('.json'):
                lang_name = lang_file[:-5]
                action = QAction(lang_name, self.main_window, checkable=True)
                action.triggered.connect(lambda checked, l=lang_name: self.change_language(l))
                if lang_name == self.current_language:
                    action.setChecked(True)
                self.main_window.lang_menu.addAction(action)


def main():
    if DEBUG:
        print("DEBUG mode on", file=sys.stderr)
    try:
        app = QApplication(sys.argv)
        settings = load_settings()
        Main(
            settings["Deduplication mode"],
            settings["Edge hiding mode"],
            settings["Mode"],
            settings["Language"],
            settings["Class"]
        )
        sys.exit(app.exec())
    except Exception as e:
        if DEBUG:
            raise
        else:
            QMessageBox.critical(None, "Error", str(e))


if __name__ == '__main__':
    main()
