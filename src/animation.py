from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ui import MainWindow

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QParallelAnimationGroup, QObject, Signal

from .constant import WINDOW_OPACITY, MODE_HIDE, MODE_SHOW
from .logger import logger


class Animation(QObject):
    started = Signal()
    finished = Signal()

    def __init__(self, parent: MainWindow, floating_window, is_left:bool, mode: str):
        super().__init__()
        logger.debug("Creating Animation (mode=%s, is_left=%s)", mode, is_left)

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
        logger.debug("Building animation window (screenshot capture)")
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
        logger.debug("Building geometry animation (left=%s)", left)
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
        if self.mode == MODE_HIDE:
            self.parent.hide()
        elif self.mode == MODE_SHOW:
            start_rect, end_rect = end_rect, start_rect
        self.geometry_animation.setStartValue(start_rect)
        self.geometry_animation.setEndValue(end_rect)

    def _build_opacity_animation(self):
        logger.debug("Building opacity animation (mode=%s)", self.mode)
        self.opacity_animation = QPropertyAnimation(self.animation_window, b'windowOpacity')
        self.opacity_animation.setDuration(1000)
        if self.mode == MODE_HIDE:
            self.opacity_animation.setStartValue(WINDOW_OPACITY)
            self.opacity_animation.setEndValue(0.0)
        elif self.mode == MODE_SHOW:
            self.animation_window.setWindowOpacity(0.0)
            self.opacity_animation.setStartValue(0.0)
            self.opacity_animation.setEndValue(WINDOW_OPACITY)

    def _build_floating_window_animation(self, mode):
        logger.debug("Building floating window opacity animation (mode=%s)", mode)
        self.floating_window_animation = QPropertyAnimation(self.floating_window, b'windowOpacity')
        self.floating_window_animation.setDuration(1000)
        self.floating_window_animation.setStartValue(0.0 if mode == MODE_HIDE else WINDOW_OPACITY)
        self.floating_window_animation.setEndValue(WINDOW_OPACITY if mode == MODE_HIDE else 0.0)

    def _build_animation_group(self, geometry_animation, opacity_animation, mode):
        logger.debug("Building parallel animation group")
        # Parallel animation group
        self.animation_group = QParallelAnimationGroup(self.parent)
        self.animation_group.addAnimation(geometry_animation)
        self.animation_group.addAnimation(opacity_animation)
        self._build_floating_window_animation(mode)
        self.animation_group.addAnimation(self.floating_window_animation)

        # Connect animation finished signal
        def _on_animation_finished():
            show_win = self.parent if self.mode == MODE_SHOW else self.floating_window
            hide_win = self.floating_window if self.mode == MODE_SHOW else self.parent
            logger.debug("Animation group finished: showing %s, hiding %s",
                         type(show_win).__name__, type(hide_win).__name__)
            show_win.show()
            hide_win.hide()
            self.finished.emit()
            self.animation_window.deleteLater()
        self.animation_group.finished.connect(_on_animation_finished)

    def build(self):
        logger.debug("Building animation components (mode=%s)", self.mode)
        self._build_animation_window()
        self._build_geometry_animation(self.is_left)
        self._build_opacity_animation()
        self._build_animation_group(self.geometry_animation, self.opacity_animation, self.mode)
        logger.debug("Animation build complete")

    def play(self):
        logger.info("Playing animation (mode=%s, is_left=%s)", self.mode, self.is_left)
        # Floating Window Settings
        self.floating_window.setWindowOpacity(0.0 if self.mode == MODE_HIDE else WINDOW_OPACITY)
        self.floating_window.show()

        self.started.emit()
        self.animation_group.start()
