from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Main, MainWindow

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QParallelAnimationGroup


class Animation:
    def __init__(self, parent: MainWindow, floating_window, is_left:bool, mode: str):
        self.parent = parent
        self.is_left = is_left
        self.mode = mode
        self.floating_window = floating_window

        # Declare variables
        self.animation_window: QWidget | None = None
        self.geometry_animation: QPropertyAnimation | None = None
        self.opacity_animation: QPropertyAnimation | None = None
        self.floating_window_animation: QPropertyAnimation | None = None
        self.animation_group: QParallelAnimationGroup | None = None

    def _build_animation_window(self):
        self.animation_window = QWidget(None)
        self.animation_window.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.animation_window.setAttribute(Qt.WA_TranslucentBackground)
        screenshot = self.parent.grab()
        image = QLabel(self.animation_window)
        image.setPixmap(screenshot.scaled(
            self.parent.width(), self.parent.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        image.show()
        self.animation_window.show()

    def _build_geometry_animation(self, left):
        self.geometry_animation = QPropertyAnimation(self.animation_window, b'geometry')
        self.geometry_animation.setDuration(1000)

        origin_x, origin_y = self.parent.x(), self.parent.y()
        origin_w, origin_h = self.parent.width(), self.parent.height()
        if left:
            start_rect = QRect(origin_x, origin_y, origin_w, origin_h)
            end_rect = QRect(origin_x, origin_y, 35, 35)
        else:
            start_rect = QRect(origin_x, origin_y, origin_w, origin_h)
            end_rect = QRect(origin_x + origin_w, origin_y, 35, 35)
        if self.mode == 'hide':
            self.parent.hide()
        elif self.mode == 'show':
            start_rect, end_rect = end_rect, start_rect
        self.geometry_animation.setStartValue(start_rect)
        self.geometry_animation.setEndValue(end_rect)

    def _build_opacity_animation(self):
        self.opacity_animation = QPropertyAnimation(self.animation_window, b'windowOpacity')
        self.opacity_animation.setDuration(1000)
        if self.mode == 'hide':
            self.opacity_animation.setStartValue(0.9)
            self.opacity_animation.setEndValue(0.0)
        elif self.mode == 'show':
            self.animation_window.setWindowOpacity(0.0)
            self.opacity_animation.setStartValue(0.0)
            self.opacity_animation.setEndValue(0.9)

    def _build_floating_window_animation(self, mode):
        self.floating_window_animation = QPropertyAnimation(self.floating_window, b'windowOpacity')
        self.floating_window_animation.setDuration(1000)
        self.floating_window_animation.setStartValue(0.0 if mode == 'hide' else 0.9)
        self.floating_window_animation.setEndValue(0.9 if mode == 'hide' else 0.0)

    def _build_animation_group(self, animate_window, geometry_animation, opacity_animation, mode):
        # Parallel animation group
        self.animation_group = QParallelAnimationGroup(self.parent)
        self.animation_group.addAnimation(geometry_animation)
        self.animation_group.addAnimation(opacity_animation)
        self._build_floating_window_animation(mode)
        self.animation_group.addAnimation(self.floating_window_animation)

        # Connect animation finished signal
        def _on_animation_finished():
            nonlocal self
            show_win = self.parent if self.mode == 'show' else self.floating_window
            hide_win = self.floating_window if self.mode == 'show' else self.parent
            show_win.show()
            hide_win.hide()
            self.parent._is_animate = False
            self.animation_window.destroy()
        self.animation_group.finished.connect(_on_animation_finished)

    def build(self):
        self._build_animation_window()
        self._build_geometry_animation(self.is_left)
        self._build_opacity_animation()
        self._build_animation_group(self.animation_window, self.geometry_animation, self.opacity_animation, self.mode)

    def play(self):
        # Floating Window Settings
        self.floating_window.setWindowOpacity(0.0 if self.mode == 'hide' else 0.9)
        self.floating_window.show()

        self.parent._is_animate = True
        self.animation_group.start()
