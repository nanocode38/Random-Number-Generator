import signal
import sys
import json
import csv
import random
import os
import time

from PySide6.QtWidgets import QApplication, QLabel, QMessageBox, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QAction, QCursor

from .constant import (
    EDGE_POS_FAULT_TOLERANCE,
    EDGE_HIDDEN_DELAY_TIME,
    DEBUG,
    APPDATA_DIR,
    CLASSES_DIR, LANGUAGE_DIR,
)
from .tools import restart, sigint_handler, load_settings, write_settings, load_language
from .animation import Animation
from .ui import MainWindow, FloatingWindow

__version__ = '1.1.0'
__author__ = 'nanocode38'

# Sentinel value for deduplication tracking
_DEDUPE_SENTINEL = -10086


class Main:
    def __init__(self, is_deduplication_mode, is_edge_hiding_mode, mode, language):
        self.is_deduplication = is_deduplication_mode
        self.is_edge_hiding = is_edge_hiding_mode
        self.current_mode = mode
        self.current_language = language
        self.language_data = load_language(language)

        # state variables
        self.number_list = set()
        self.selected_class = ''
        self.class_names = []

        # Edge hiding related
        self.floating_window: FloatingWindow | None = None
        self.activate_timer = 0.0
        self.cross_the_boundary_timer = 0.0
        if self.is_edge_hiding:
            self._setup_floating_window()

        # Create Main Window
        self.main_window = MainWindow(self.language_data, mode)
        self.main_window.apply_theme(mode)

        # Create Main Window Widgets
        self._set_widgets_state()

        # Main loop timer (replace while True)
        self.main_timer = QTimer(self.main_window)
        self.main_timer.timeout.connect(self._main_loop_step)
        self.main_timer.start(50)  # Check every 50ms

        # Animate Flag
        self._is_animate = False

        # Burying the debug forced interrupt listener
        if DEBUG:
            signal.signal(signal.SIGINT, sigint_handler)  # Take over SIGINT
            timer = QTimer()
            timer.start(500)  # Run the interpreter every 500ms
            timer.timeout.connect(lambda: None)  # Signal callback

        self.main_window.show()
        QApplication.instance().aboutToQuit.connect(self.save_settings)

    def on_class_changed(self, text):
        self.selected_class = text

    def on_hide_mode_changed(self, state):
        self.is_edge_hiding = (Qt.CheckState(state) == Qt.Checked)
        if self.is_edge_hiding and not self.floating_window:
            self._setup_floating_window()
        self.main_window.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_edge_hiding)
        self.main_window.show()
        if not self.is_edge_hiding:
            self.cross_the_boundary_timer = 0.0
            if self.floating_window:
                self.floating_window.hide()

    def make_random(self):
        cls = self.selected_class or 'example'
        filepath = CLASSES_DIR / f'{cls}.csv'
        if not os.path.exists(filepath):
            QMessageBox.warning(self.main_window, self.language_data["Class file error title"],
                                f'{self.language_data["Class file error"]} {filepath}')
            return
        with open(filepath, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        if not rows:
            return
        names = rows[0]  # Assume there is only one line of names
        n = len(names)

        if self.main_window.dedup_check.isChecked():
            # If everyone has been drawn
            if len(self.number_list) >= n:
                QMessageBox.information(self.main_window, self.language_data['Title'],
                                        self.language_data['Message'])
                self.number_list.clear()
                return
            idx = random.randint(0, n - 1)
            while idx in self.number_list:
                idx = random.randint(0, n - 1)
        else:
            idx = random.randint(0, n - 1)

        self.number_list.add(idx)
        self.main_window.num_label.setText(str(idx + 1))
        self.main_window.name_label.setText(names[idx])

    def change_language(self, language):
        try:
            language_file = LANGUAGE_DIR / f'{language}.json'
            with open(language_file, encoding='utf-8') as fp:
                self.language_data = json.load(fp)
        except Exception as e:
            QMessageBox.critical(self.main_window, self.language_data['Title'],
                                 self.language_data['Language Error'].format(type=type(e).__name__,
                                                                             e=e, id=hex(id(e))))
            raise
        else:
            self.current_language = language
            if QMessageBox.question(self.main_window, self.language_data['Title'],
                                    self.language_data['Restart Info']) == QMessageBox.Yes:
                self.save_settings()
                restart()

    def _setup_floating_window(self):
        self.floating_window = FloatingWindow(None)
        self.floating_window.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.floating_window.setAttribute(Qt.WA_TranslucentBackground)
        self.floating_window.resize(50, 50)
        # Add icons
        icon_label = QLabel(self.floating_window)
        pixmap = QPixmap(str(APPDATA_DIR / 'icon.png')).scaled(40, 40, Qt.KeepAspectRatio)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self.floating_window)
        layout.addWidget(icon_label)
        self.floating_window.hide()

        # binding events
        def _on_enter():
            self.activate_timer = time.time()

        def _on_leave():
            self.activate_timer = 0.0

        self.floating_window.enter.connect(_on_enter)
        self.floating_window.leave.connect(_on_leave)
        self.floating_window.mouse_button_press.connect(lambda: self.check_activate(force=True))

    def _main_loop_step(self):
        """Operations performed per frame"""
        self.check_cross_the_boundary()
        self.check_activate()

    def check_cross_the_boundary(self):
        if not self.is_edge_hiding:
            return
        if self.floating_window and self.floating_window.isVisible():
            return
        if self._is_animate:
            return

        x = self.main_window.x()
        y = self.main_window.y()
        w = self.main_window.width()
        screen = self.main_window.screen()
        screen_w = screen.size().width() if screen else 1920

        near_left = x < EDGE_POS_FAULT_TOLERANCE
        near_right = x > screen_w - w - EDGE_POS_FAULT_TOLERANCE

        if (not near_left and not near_right) or self._mouse_in_window():
            self.cross_the_boundary_timer = 0.0
            return

        if near_left or near_right:
            if self.cross_the_boundary_timer == 0.0:
                self.cross_the_boundary_timer = time.time()
            elif time.time() - self.cross_the_boundary_timer >= EDGE_HIDDEN_DELAY_TIME:
                if near_left:
                    fx = -self.floating_window.width() // 4
                else:
                    fx = screen_w - EDGE_POS_FAULT_TOLERANCE - self.floating_window.width() + 5
                fy = y
                self.floating_window.move(fx, fy)
                # Play hide animation
                animation = Animation(self.main_window, self.floating_window, near_left, 'hide')
                animation.started.connect(lambda: setattr(self, '_is_animate', True))
                animation.finished.connect(lambda: setattr(self, '_is_animate', False))
                animation.build()
                animation.play()

    def check_activate(self, force=False):
        if not self.is_edge_hiding:
            return
        if force or (self.activate_timer != 0.0 and time.time() - self.activate_timer >= EDGE_HIDDEN_DELAY_TIME):
            # Restore the main window
            self.floating_window.hide()
            animation = Animation(self.main_window, self.floating_window, self.main_window.x() <= 15, 'show')
            animation.started.connect(lambda: setattr(self, '_is_animate', True))
            animation.finished.connect(lambda: setattr(self, '_is_animate', False))
            animation.build()
            animation.play()
            self.activate_timer = 0.0
            self.cross_the_boundary_timer = 0.0

    def _mouse_in_window(self):
        return self.main_window.frameGeometry().contains(QCursor.pos())

    def save_settings(self):
        write_settings(
            self.main_window.dedup_check.isChecked(),
            self.main_window.hide_check.isChecked(),
            self.current_mode,
            self.current_language
        )

    def _set_widgets_state(self):
        # Load class list
        for file in os.listdir(CLASSES_DIR):
            if file.endswith('.csv'):
                self.class_names.append(file.replace('.csv', ''))

        self.main_window.class_combo.addItems(self.class_names)
        self.main_window.class_combo.currentTextChanged.connect(self.on_class_changed)
        self.main_window.dedup_check.setChecked(self.is_deduplication)
        self.main_window.hide_check.setChecked(self.is_edge_hiding)
        self.main_window.hide_check.stateChanged.connect(self.on_hide_mode_changed)
        self.main_window.random_btn.clicked.connect(self.make_random)
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
        Main(settings["Deduplication mode"], settings["Edge hiding mode"], settings["Mode"], settings["Language"])
        sys.exit(app.exec())
    except Exception as e:
        if DEBUG:
            raise
        else:
            QMessageBox.critical(None, "Error", str(e))


if __name__ == '__main__':
    main()