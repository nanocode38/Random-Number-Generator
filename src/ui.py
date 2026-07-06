from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QComboBox,
    QCheckBox, QPushButton, QMessageBox,
    QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics, QIcon, QAction

from .constant import (
    ROOT_WINDOW_WIDTH,
    ROOT_WINDOW_HEIGHT,
    DEBUG,
    APPDATA_DIR,
    WINDOW_OPACITY, STYLE_DIR

)

__all__ = [
    'MainWindow',
    'FloatingWindow'
]

class MainWindow(QMainWindow):
    def __init__(self, language_data, mode):
        super().__init__()

        self.language_data = language_data
        self.current_mode = mode

        # Window basic settings
        self.setWindowTitle(self.language_data['Title'])
        self.setWindowOpacity(WINDOW_OPACITY)
        if DEBUG:
            self.resize(ROOT_WINDOW_WIDTH, ROOT_WINDOW_HEIGHT)
        else:
            self.setFixedSize(ROOT_WINDOW_WIDTH, ROOT_WINDOW_HEIGHT)
        self.setWindowIcon(QIcon(str(APPDATA_DIR / 'icon.ico')))

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

        # Calculate fixed width for 9 half-width characters
        _label_font = QFont('Times', 24, QFont.Bold)
        _fm = QFontMetrics(_label_font)
        _box_width = _fm.averageCharWidth() * 9 + 28  # +24 padding + 4 border

        self.num_label = QLabel('')
        self.num_label.setObjectName('num_label')
        self.num_label.setFont(_label_font)
        self.num_label.setAlignment(Qt.AlignCenter)
        self.num_label.setFixedWidth(_box_width)

        self.name_label = QLabel('')
        self.name_label.setObjectName('name_label')
        self.name_label.setFont(_label_font)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setFixedWidth(_box_width)

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
        self.mode_menu = menubar.addMenu(self.language_data['Mode'])

        # Language menu
        self.lang_menu = menubar.addMenu(self.language_data['Language'])

    def change_mode(self, mode):
        self.current_mode = mode
        self.apply_theme(mode)

    def apply_theme(self, mode):
        with open (STYLE_DIR / f'{mode}.css', 'r') as f:
            self.setStyleSheet(f.read())

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
    entered = Signal()
    exited = Signal()
    mouse_button_press = Signal()

    def enterEvent(self, event):
        self.entered.emit()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.exited.emit()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.mouse_button_press.emit()
        super().mousePressEvent(event)
