import sys
import json
import csv
import random
import os
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QComboBox,
    QCheckBox, QPushButton, QMessageBox,
    QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer, QPoint, QRect, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap, QAction, QMouseEvent
import pyautogui as pyg

from constant import (
    EDGE_POS_FAULT_TOLERANCE,
    EDGE_HIDDEN_DELAY_TIME,
    ROOT_WINDOW_WIDTH,
    ROOT_WINDOW_HEIGHT
)



class MainWindow(QMainWindow):
    def __init__(self, is_deduplication_mode, is_edge_hiding_mode, mode, language):
        super().__init__()
        self.language_data = {}
        self.is_deduplication = is_deduplication_mode
        self.is_edge_hiding = is_edge_hiding_mode
        self.current_mode = mode
        self.current_language = language

        # 加载语言
        self.load_language(language)

        # 窗口基本设置
        self.setWindowTitle(self.language_data['Title'])
        self.setFixedSize(ROOT_WINDOW_WIDTH, ROOT_WINDOW_HEIGHT)
        self.setWindowIcon(QIcon('AppData/icon.ico'))

        # 状态变量
        self.number_list = {-10086}
        self.selected_class = ''
        self.class_names = []

        # 创建控件
        self._create_widgets()
        self._create_menu()

        # 边缘隐藏相关
        self.floating_window: Optional[QWidget] = None
        self.activate_timer = 0.0
        self.cross_the_boundary_timer = 0.0
        if self.is_edge_hiding:
            self._setup_floating_window()

        # 主循环定时器（替代 while True）
        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self._main_loop_step)
        self.main_timer.start(50)  # 每 50ms 检查一次

        # 应用主题
        self.apply_theme(mode)

    def load_language(self, lang):
        with open(f'AppData/language/{lang}.json', encoding='utf-8') as f:
            self.language_data = json.load(f)

    def _create_widgets(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 顶部区域：班级选择 + 复选框
        top_layout = QHBoxLayout()
        self.class_label = QLabel(self.language_data['Class'] + ': ')
        self.class_combo = QComboBox()
        self.class_combo.setEditable(False)
        # 加载班级列表
        for f in os.listdir('Classes/'):
            if f.endswith('.csv'):
                self.class_names.append(f.replace('.csv', ''))
        self.class_combo.addItems(self.class_names)
        self.class_combo.currentTextChanged.connect(self.on_class_changed)

        self.dedup_check = QCheckBox(self.language_data['Deduplication'])
        self.dedup_check.setChecked(self.is_deduplication)

        self.hide_check = QCheckBox(self.language_data['Hide'])
        self.hide_check.setChecked(self.is_edge_hiding)
        self.hide_check.stateChanged.connect(self.on_hide_mode_changed)

        top_layout.addWidget(self.class_label)
        top_layout.addWidget(self.class_combo)
        top_layout.addWidget(self.dedup_check)
        top_layout.addWidget(self.hide_check)
        layout.addLayout(top_layout)

        # 中间显示数字和姓名
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

        # 底部按钮
        self.random_btn = QPushButton(self.language_data['Button Text'])
        self.random_btn.setFont(QFont('Times', 28, QFont.Bold))
        self.random_btn.clicked.connect(self.make_random)
        layout.addWidget(self.random_btn, alignment=Qt.AlignBottom)

    def _create_menu(self):
        menubar = self.menuBar()

        # 关于菜单
        about_menu = menubar.addMenu(self.language_data['About'])
        help_action = QAction(self.language_data['Help'], self)
        help_action.triggered.connect(self.show_help)
        about_action = QAction(self.language_data['About'], self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(help_action)
        about_menu.addAction(about_action)

        # 模式菜单
        mode_menu = menubar.addMenu(self.language_data['Mode'])
        light_action = QAction(self.language_data['Light'], self)
        light_action.triggered.connect(lambda: self.change_mode('Light'))
        dark_action = QAction(self.language_data['Dark'], self)
        dark_action.triggered.connect(lambda: self.change_mode('Dark'))
        mode_menu.addAction(light_action)
        mode_menu.addAction(dark_action)

        # 语言菜单（单选）
        lang_menu = menubar.addMenu(self.language_data['Language'])
        self.lang_actions = []
        for lang_file in os.listdir('AppData/language'):
            if lang_file.endswith('.json'):
                lang_name = lang_file[:-5]
                action = QAction(lang_name, self, checkable=True)
                action.triggered.connect(lambda checked, l=lang_name: self.change_language(l))
                if lang_name == self.current_language:
                    action.setChecked(True)
                lang_menu.addAction(action)
                self.lang_actions.append(action)

    def on_class_changed(self, text):
        self.selected_class = text

    def on_hide_mode_changed(self, state):
        self.is_edge_hiding = (state == Qt.Checked)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_edge_hiding)
        if not self.is_edge_hiding:
            self.cross_the_boundary_timer = 0.0
            if self.floating_window:
                self.floating_window.hide()

    def make_random(self):
        cls = self.selected_class or 'example'
        filepath = f'Classes/{cls}.csv'
        if not os.path.exists(filepath):
            QMessageBox.warning(self, '错误', f'找不到班级文件 {filepath}')
            return
        with open(filepath, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        if not rows:
            return
        names = rows[0]  # 假设只有一行名字
        n = len(names)

        if self.dedup_check.isChecked():
            # 如果已经抽完所有人
            if len(self.number_list) - 1 >= n:  # 排除 -10086
                QMessageBox.information(self, self.language_data['Title'],
                                        self.language_data['Message'])
                self.number_list = {-10086}
                return
            idx = random.randint(0, n - 1)
            while idx in self.number_list:
                idx = random.randint(0, n - 1)
        else:
            idx = random.randint(0, n - 1)

        self.number_list.add(idx)
        self.num_label.setText(str(idx + 1))
        self.name_label.setText(names[idx])

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

    def change_language(self, lang):
        try:
            self.load_language(lang)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load language: {e}')
            return
        reply = QMessageBox.question(self, self.language_data['Title'],
                                     self.language_data['Restart Info'],
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save_settings()
            # 重启（这里可以用 QProcess 启动自身，简单起见提示用户手动重启）
            QApplication.quit()
            # 实际项目中可调用 os.execl(sys.executable, ...)
        else:
            # 更新 UI 文本（略复杂，可重新构建窗口或逐个更新）
            pass

    def show_help(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('帮助')
        dlg.setText(self.language_data['Help Text'])
        dlg.exec()

    def show_about(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('关于')
        dlg.setText(self.language_data['About Text'])
        dlg.exec()

    def _setup_floating_window(self):
        self.floating_window = QWidget(None)
        self.floating_window.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.floating_window.setAttribute(Qt.WA_TranslucentBackground)
        self.floating_window.resize(50, 50)
        # 添加图标
        icon_label = QLabel(self.floating_window)
        pixmap = QPixmap('AppData/icon.png').scaled(40, 40, Qt.KeepAspectRatio)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self.floating_window)
        layout.addWidget(icon_label)
        self.floating_window.hide()

        # 绑定事件
        self.floating_window.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.floating_window:
            if event.type() == QMouseEvent.Type.Enter:
                self.activate_timer = time.time()
            elif event.type() == QMouseEvent.Type.Leave:
                self.activate_timer = 0.0
            elif event.type() == QMouseEvent.Type.MouseButtonPress:
                self.check_activate(force=True)
        return super().eventFilter(obj, event)

    def _main_loop_step(self):
        """每帧执行的操作"""
        self.check_cross_the_boundary()
        self.check_activate()

    def check_cross_the_boundary(self):
        if not self.is_edge_hiding or self._mouse_in_window():
            return
        if self.floating_window and self.floating_window.isVisible():
            return

        x = self.x()
        y = self.y()
        w = self.width()
        screen_w = self.screen().size().width()
        screen_h = self.screen().size().height()

        near_left = x < EDGE_POS_FAULT_TOLERANCE
        near_right = x > screen_w - w - EDGE_POS_FAULT_TOLERANCE

        if not near_left and not near_right:
            self.cross_the_boundary_timer = 0.0
            return

        if near_left or near_right:
            if self.cross_the_boundary_timer == 0.0:
                self.cross_the_boundary_timer = time.time()
            elif time.time() - self.cross_the_boundary_timer >= EDGE_HIDDEN_DELAY_TIME:
                # 隐藏主窗口，显示浮动窗口
                self.hide()
                if near_left:
                    fx = EDGE_POS_FAULT_TOLERANCE
                else:
                    fx = screen_w - EDGE_POS_FAULT_TOLERANCE - self.floating_window.width()
                fy = y
                self.floating_window.move(fx, fy)
                self.floating_window.show()
                # 动画效果（简化：直接用透明度变化）
                self._play_hide_animation(near_left)

    def check_activate(self, force=False):
        if not self.is_edge_hiding:
            return
        if force or (self.activate_timer != 0.0 and time.time() - self.activate_timer >= EDGE_HIDDEN_DELAY_TIME):
            # 恢复主窗口
            self.showNormal()
            self.floating_window.hide()
            self.activate_timer = 0.0
            self.cross_the_boundary_timer = 0.0

    def _mouse_in_window(self):
        mx, my = pyg.position()
        wx, wy = self.x(), self.y()
        ww, wh = self.width(), self.height()
        # 允许上方 80px 容差
        if wx <= mx <= wx + ww and wy - 80 <= my <= wy + wh:
            self.cross_the_boundary_timer = 0.0
            return True
        return False

    def _play_hide_animation(self, left):
        # 简单的缩放动画（可用 QPropertyAnimation）
        # 这里略过具体实现，保持功能即可
        pass

    def save_settings(self):
        data = {
            'Deduplication mode': self.dedup_check.isChecked(),
            'Edge hiding mode': self.hide_check.isChecked(),
            'Language': self.current_language,
            'Mode': self.current_mode
        }
        with open('AppData/data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 读取配置
    with open('AppData/data.json', encoding='utf-8') as f:
        data = json.load(f)
    window = MainWindow(
        is_deduplication_mode=data['Deduplication mode'],
        is_edge_hiding_mode=data['Edge hiding mode'],
        mode=data['Mode'],
        language=data['Language']
    )
    window.show()
    sys.exit(app.exec())