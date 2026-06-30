import signal
import sys
import json
import csv
import random
import os
import time
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QComboBox,
    QCheckBox, QPushButton, QMessageBox,
    QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QParallelAnimationGroup, Signal, QEvent
from PySide6.QtGui import QFont, QIcon, QPixmap, QAction, QMouseEvent, QCursor

from .constant import (
    EDGE_POS_FAULT_TOLERANCE,
    EDGE_HIDDEN_DELAY_TIME,
    ROOT_WINDOW_WIDTH,
    ROOT_WINDOW_HEIGHT,
    DEBUG
)
from .tools import restart, sigint_handler, load_settings, write_settings, load_language
from .animation import Animation


__version__ = '1.1.0'
__author__ = 'nanocode38'

class MainWindow(QMainWindow):
    def __init__(self, language_data, mode):
        super().__init__()

        self.language_data = language_data
        self.current_mode = mode

        # Window basic settings
        self.setWindowTitle(self.language_data['Title'])
        self.setWindowOpacity(0.9)
        if DEBUG:
            self.resize(ROOT_WINDOW_WIDTH, ROOT_WINDOW_HEIGHT)
        else:
            self.setFixedSize(ROOT_WINDOW_WIDTH, ROOT_WINDOW_HEIGHT)
        self.setWindowIcon(QIcon('AppData/icon.ico'))

        # Create controls
        self._create_widgets()
        self._create_menu()

    def _create_widgets(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Top area: class selection + checkbox
        top_layout = QHBoxLayout()
        self.class_label = QLabel(self.language_data['Class'] + ': ')
        self.class_combo = QComboBox()
        self.class_combo.setEditable(False)


        self.dedup_check = QCheckBox(self.language_data['Deduplication'])

        self.hide_check = QCheckBox(self.language_data['Hide'])

        top_layout.addWidget(self.class_label)
        top_layout.addWidget(self.class_combo)
        top_layout.addWidget(self.dedup_check)
        top_layout.addWidget(self.hide_check)
        layout.addLayout(top_layout)

        # Middle area: display number and name
        middle_layout = QHBoxLayout()
        self.num_label = QLabel('')
        self.num_label.setFont(QFont('Times', 48, QFont.Bold))
        self.num_label.setAlignment(Qt.AlignCenter)
        self.num_label.setStyleSheet('color: blue;')

        self.name_label = QLabel('')
        self.name_label.setFont(QFont('Times', 32, QFont.Bold))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet('color: blue;')

        middle_layout.addWidget(self.num_label)
        middle_layout.addWidget(self.name_label)
        layout.addLayout(middle_layout)

        # Bottom buttons
        self.random_btn = QPushButton(self.language_data['Button Text'])
        self.random_btn.setFont(QFont('Times', 28, QFont.Bold))
        layout.addWidget(self.random_btn, alignment=Qt.AlignBottom)

    def _create_menu(self):
        menubar = self.menuBar()

        # About menu
        about_menu = menubar.addMenu(self.language_data['About'])
        help_action = QAction(self.language_data['Help'], self)
        help_action.triggered.connect(self.show_help)
        about_action = QAction(self.language_data['About'], self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(help_action)
        about_menu.addAction(about_action)

        # Mode menu
        mode_menu = menubar.addMenu(self.language_data['Mode'])
        light_action = QAction(self.language_data['Light'], self)
        light_action.triggered.connect(lambda: self.change_mode('Light'))
        dark_action = QAction(self.language_data['Dark'], self)
        dark_action.triggered.connect(lambda: self.change_mode('Dark'))
        mode_menu.addAction(light_action)
        mode_menu.addAction(dark_action)

        # Language menu (radio buttons)
        self.lang_menu = menubar.addMenu(self.language_data['Language'])
        # self.lang_actions = []

    def change_mode(self, mode):
        self.current_mode = mode
        self.apply_theme(mode)

    def apply_theme(self, mode):
        if mode == 'Dark':
            self.setStyleSheet('''
                QMainWindow { background-color: #222; color: white; }
                QLabel { color: white; }
                QPushButton { background-color: #555; color: white; }
            ''')
        else:
            self.setStyleSheet('''
                QMainWindow { background-color: #fff; color: black; }
                QLabel { color: black; }
                QPushButton { background-color: #e0e0e0; color: black; }
            ''')

    def show_help(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(self.language_data['Help Window Title'])
        dlg.setText(self.language_data['Help Text'])
        dlg.exec()

    def show_about(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(self.language_data['About'])
        dlg.setText(self.language_data['About Text'])
        dlg.exec()

class FloatingWindow(QWidget):
    enter = Signal()
    leave = Signal()
    mouse_button_press = Signal()

    def enterEvent(self, event):
        self.enter.emit()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.leave.emit()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.mouse_button_press.emit()
        super().mousePressEvent(event)

class Main:
    def __init__(self, is_deduplication_mode, is_edge_hiding_mode, mode, language):
        super().__init__()

        self.is_deduplication = is_deduplication_mode
        self.is_edge_hiding = is_edge_hiding_mode
        self.current_mode = mode
        self.current_language = language
        self.language_data = load_language(language)

        # state variables
        self.number_list = {-10086}
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

    def load_language(self, lang):
        with open(f'AppData/language/{lang}.json', encoding='utf-8') as f:
            self.language_data = json.load(f)

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
        filepath = f'Classes/{cls}.csv'
        if not os.path.exists(filepath):
            QMessageBox.warning(self.main_window, self.language_data["Class file error title"], f'{self.language_data["Class file error"]} {filepath}')
            return
        with open(filepath, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        if not rows:
            return
        names = rows[0]  # Assume there is only one line of names
        n = len(names)

        if self.main_window.dedup_check.isChecked():
            # If everyone has been drawn
            if len(self.number_list) - 1 >= n:  # except -10086
                QMessageBox.information(self.main_window, self.language_data['Title'],
                                        self.language_data['Message'])
                self.number_list = {-10086}
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
            with open('AppData/language/' + language + '.json', encoding='utf-8') as fp:
                self.language = json.load(fp)
        except Exception as e:
            QMessageBox.critical(self.main_window, self.language['Title'], self.language['Language Error'].format(type=type(e).__name__,
                                                                                                e=e, id=hex(id(e))))
            raise e
        else:
            self.current_language = language
            if QMessageBox.question(self.main_window, self.language['Title'], self.language['Restart Info']) == QMessageBox.Yes:
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
        pixmap = QPixmap('AppData/icon.png').scaled(40, 40, Qt.KeepAspectRatio)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self.floating_window)
        layout.addWidget(icon_label)
        self.floating_window.hide()

        # binding events
        def _on_enter():
            nonlocal self
            self.activate_timer = time.time()

        def _on_leave():
            nonlocal self
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
        screen_w = self.main_window.screen().size().width()

        near_left = x < EDGE_POS_FAULT_TOLERANCE
        near_right = x > screen_w - w - EDGE_POS_FAULT_TOLERANCE

        if not near_left and not near_right  or self._mouse_in_window():
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
                animation.build()
                animation.play()

    def check_activate(self, force=False):
        if not self.is_edge_hiding:
            return
        if force or (self.activate_timer != 0.0 and time.time() - self.activate_timer >= EDGE_HIDDEN_DELAY_TIME):
            # Restore the main window
            self.floating_window.hide()
            animation = Animation(self.main_window, self.floating_window, self.main_window.x() <= 15, 'show')
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
        for file in os.listdir('Classes/'):
            if file.endswith('.csv'):
                self.class_names.append(file.replace('.csv', ''))

        self.main_window.class_combo.addItems(self.class_names)
        self.main_window.class_combo.currentTextChanged.connect(self.on_class_changed)
        self.main_window.dedup_check.setChecked(self.is_deduplication)
        self.main_window.hide_check.setChecked(self.is_edge_hiding)
        self.main_window.hide_check.stateChanged.connect(self.on_hide_mode_changed)
        self.main_window.random_btn.clicked.connect(self.make_random)
        for lang_file in os.listdir('AppData/language'):
            if lang_file.endswith('.json'):
                lang_name = lang_file[:-5]
                action = QAction(lang_name, self.main_window, checkable=True)
                action.triggered.connect(lambda checked, l=lang_name: self.change_language(l))
                if lang_name == self.current_language:
                    action.setChecked(True)
                self.main_window.lang_menu.addAction(action)



def main():
    global DEBUG
    if DEBUG:
        print("DEBUG mode on", file=sys.stderr)
    try:
        app = QApplication(sys.argv)
        settings = load_settings()
        Main(settings["Deduplication mode"], settings["Edge hiding mode"], settings["Mode"], settings["Language"])
        sys.exit(app.exec())
    except Exception as e:
        if DEBUG:
            raise e


if __name__ == '__main__':
    main()