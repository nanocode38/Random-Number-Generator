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
from .logger import logger

__version__ = '1.1.0'
__author__ = 'nanocode38'


class Main:
    """Lightweight coordinator that wires together the main window,
    student picker, and edge hider.
    """

    def __init__(self, is_deduplication_mode, is_edge_hiding_mode, mode, language, class_):
        logger.info("Initializing application (mode=%s, language=%s, class=%s)", mode, language, class_)

        self.current_mode = mode
        self.current_language = language
        logger.debug("Loading language data: %s", language)
        self.language_data = load_language(language)

        # Create main window
        logger.debug("Creating main window")
        self.main_window = MainWindow(self.language_data, mode)
        logger.debug("Applying theme: %s", mode)
        self.main_window.apply_theme(mode)

        # Create components
        logger.debug("Creating StudentPicker component")
        self.picker = StudentPicker(self.main_window, self.language_data, class_)
        logger.debug("Creating EdgeHider component")
        self.edge_hider = EdgeHider(self.main_window)

        # Wire up widgets
        logger.debug("Wiring up widgets (dedup=%s, edge_hiding=%s)", is_deduplication_mode, is_edge_hiding_mode)
        self._set_widgets_state(is_deduplication_mode, is_edge_hiding_mode)

        # Enable edge hiding if configured
        if is_edge_hiding_mode:
            logger.info("Edge hiding mode enabled at startup")
            self.edge_hider.enable()

        # Debug: allow Ctrl+C to interrupt
        if DEBUG:
            logger.debug("Registering SIGINT handler and keepalive timer for DEBUG mode")
            signal.signal(signal.SIGINT, sigint_handler)
            timer = QTimer()
            timer.start(500)
            timer.timeout.connect(lambda: None)

        self.main_window.show()
        logger.info("Main window shown, entering event loop")

        QApplication.instance().aboutToQuit.connect(self.save_settings)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def save_settings(self):
        logger.info("Saving settings on application quit")
        write_settings(
            self.main_window.dedup_check.isChecked(),
            self.main_window.hide_check.isChecked(),
            self.current_mode,
            self.current_language,
            self.picker.selected_class
        )
        logger.debug("Settings saved: mode=%s, language=%s, class=%s",
                      self.current_mode, self.current_language, self.picker.selected_class)

    # ------------------------------------------------------------------
    # Language switching
    # ------------------------------------------------------------------

    def change_language(self, language):
        logger.info("Attempting to change language to: %s", language)
        try:
            language_file = LANGUAGE_DIR / f'{language}.json'
            logger.debug("Loading language file: %s", language_file)
            with open(language_file, encoding='utf-8') as fp:
                self.language_data = json.load(fp)
        except Exception as e:
            logger.error("Failed to load language file '%s': %s", language_file, e, exc_info=True)
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
            logger.debug("Language data loaded successfully, prompting user for restart")
            if (
                QMessageBox.question(
                    self.main_window,
                    self.language_data['Title'],
                    self.language_data['Restart Info'],
                )
                == QMessageBox.Yes
            ):
                logger.info("User confirmed restart for language switch")
                self.save_settings()
                restart()
            else:
                logger.debug("User declined restart")

    # ------------------------------------------------------------------
    # Edge-hiding toggle
    # ------------------------------------------------------------------

    def on_hide_mode_changed(self, state):
        is_edge_hiding = Qt.CheckState(state) == Qt.Checked
        logger.info("Edge hiding mode toggled: %s", is_edge_hiding)
        if is_edge_hiding:
            self.edge_hider.enable()
        else:
            self.edge_hider.disable()

    # ------------------------------------------------------------------
    # Widget wiring
    # ------------------------------------------------------------------

    def _set_widgets_state(self, is_deduplication_mode, is_edge_hiding_mode):
        # Class combo
        logger.debug("Populating class combo with %d classes", len(self.picker.class_names))
        self.main_window.class_combo.addItems(self.picker.class_names)
        self.main_window.class_combo.currentTextChanged.connect(self.picker.on_class_changed)

        # Checkboxes
        self.main_window.dedup_check.setChecked(is_deduplication_mode)
        self.main_window.hide_check.setChecked(is_edge_hiding_mode)
        self.main_window.hide_check.stateChanged.connect(self.on_hide_mode_changed)
        logger.debug("Checkboxes initialized (dedup=%s, edge_hiding=%s)",
                      is_deduplication_mode, is_edge_hiding_mode)

        # Random button
        self.main_window.random_btn.clicked.connect(self.picker.make_random)

        # Mode menu
        mode_count = 0
        for mode in STYLE_DIR.iterdir():
            if not mode.name.endswith('.css'):
                continue
            mode = mode.stem
            mode_count += 1
            action = QAction(mode, self.main_window, checkable=False)
            action.triggered.connect(lambda checked, m=mode: self.main_window.change_mode(m))
            self.main_window.mode_menu.addAction(action)
        logger.debug("Mode menu populated with %d themes", mode_count)

        # Language menu
        lang_count = 0
        for lang_file in os.listdir(LANGUAGE_DIR):
            if lang_file.endswith('.json'):
                lang_name = lang_file[:-5]
                lang_count += 1
                action = QAction(lang_name, self.main_window, checkable=True)
                action.triggered.connect(lambda checked, l=lang_name: self.change_language(l))
                if lang_name == self.current_language:
                    action.setChecked(True)
                self.main_window.lang_menu.addAction(action)
        logger.debug("Language menu populated with %d languages", lang_count)


def main():
    logger.info("=== Application starting (version %s) ===", __version__)
    logger.debug("DEBUG mode: %s", DEBUG)

    if DEBUG:
        print("DEBUG mode on", file=sys.stderr)
    try:
        app = QApplication(sys.argv)
        logger.debug("QApplication instance created")
        settings = load_settings()
        logger.debug("Settings loaded: %s", settings)
        Main(
            settings["Deduplication mode"],
            settings["Edge hiding mode"],
            settings["Mode"],
            settings["Language"],
            settings["Class"]
        )
        logger.info("Entering Qt event loop")
        sys.exit(app.exec())
    except Exception as e:
        logger.critical("Unhandled exception in main: %s", e, exc_info=True)
        if DEBUG:
            raise
        else:
            QMessageBox.critical(None, "Error", str(e))


if __name__ == '__main__':
    main()
