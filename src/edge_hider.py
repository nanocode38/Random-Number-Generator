from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ui import MainWindow, FloatingWindow

from PySide6.QtWidgets import QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QCursor

from .constant import (
    EDGE_POS_FAULT_TOLERANCE,
    EDGE_HIDDEN_DELAY_TIME,
    APPDATA_DIR,
    MODE_HIDE,
    MODE_SHOW,
)
from .animation import Animation


class EdgeHider:
    """Manages edge-hiding behaviour: detects when the main window is near
    screen edges, hides it with an animation, and shows a floating icon
    that restores the window on interaction.
    """

    def __init__(self, main_window: MainWindow):
        self.main_window = main_window
        self.floating_window: FloatingWindow | None = None
        self._is_animate = False
        self._activate_timer = 0.0
        self._boundary_timer = 0.0

        # Polling timer — checks edge proximity every 50 ms
        self._timer = QTimer(main_window)
        self._timer.timeout.connect(self._tick)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enable(self):
        """Start edge-hiding mode."""
        if not self.floating_window:
            self._setup_floating_window()
        self.main_window.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.main_window.show()
        self._timer.start(50)

    def disable(self):
        """Stop edge-hiding mode and restore visibility."""
        self._timer.stop()
        self._boundary_timer = 0.0
        if self.floating_window:
            self.floating_window.hide()
        self.main_window.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.main_window.show()

    # ------------------------------------------------------------------
    # Internal — floating window setup
    # ------------------------------------------------------------------

    def _setup_floating_window(self):
        from .ui import FloatingWindow

        fw = FloatingWindow(None)
        fw.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        fw.setAttribute(Qt.WA_TranslucentBackground)
        fw.resize(50, 50)

        icon_label = QLabel(fw)
        pixmap = QPixmap(str(APPDATA_DIR / 'icon.png')).scaled(40, 40, Qt.KeepAspectRatio)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(fw)
        layout.addWidget(icon_label)
        fw.hide()

        fw.entered.connect(self._on_float_enter)
        fw.exited.connect(self._on_float_leave)
        fw.mouse_button_press.connect(lambda: self._check_activate(force=True))

        self.floating_window = fw

    # ------------------------------------------------------------------
    # Internal — polling loop
    # ------------------------------------------------------------------

    def _tick(self):
        self._check_boundary()
        self._check_activate()

    def _check_boundary(self):
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
            self._boundary_timer = 0.0
            return

        if self._boundary_timer == 0.0:
            self._boundary_timer = time.time()
        elif time.time() - self._boundary_timer >= EDGE_HIDDEN_DELAY_TIME:
            if near_left:
                fx = -self.floating_window.width() // 4
            else:
                fx = screen_w - EDGE_POS_FAULT_TOLERANCE - self.floating_window.width() + 5
            self.floating_window.move(fx, y)

            animation = Animation(self.main_window, self.floating_window, near_left, MODE_HIDE)
            animation.started.connect(self._on_anim_start)
            animation.finished.connect(self._on_anim_finish)
            animation.build()
            animation.play()

    def _check_activate(self, force=False):
        if force or (self._activate_timer != 0.0
                     and time.time() - self._activate_timer >= EDGE_HIDDEN_DELAY_TIME):
            self.floating_window.hide()
            animation = Animation(
                self.main_window, self.floating_window,
                self.main_window.x() <= 15, MODE_SHOW,
            )
            animation.started.connect(self._on_anim_start)
            animation.finished.connect(self._on_anim_finish)
            animation.build()
            animation.play()
            self._activate_timer = 0.0
            self._boundary_timer = 0.0

    # ------------------------------------------------------------------
    # Internal — helpers
    # ------------------------------------------------------------------

    def _mouse_in_window(self):
        return self.main_window.frameGeometry().contains(QCursor.pos())

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_float_enter(self):
        self._activate_timer = time.time()

    def _on_float_leave(self):
        self._activate_timer = 0.0

    def _on_anim_start(self):
        self._is_animate = True

    def _on_anim_finish(self):
        self._is_animate = False
