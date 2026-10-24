from typing import Optional

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QCursor, QScreen
from PyQt5.QtWidgets import QApplication


def getCurrentScreen() -> Optional[QScreen]:
    """get current screen"""
    cursorPos: QPoint = QCursor.pos()

    for s in QApplication.screens():
        if s.geometry().contains(cursorPos):
            return s

    return None


def getCurrentScreenGeometry(available: bool = True) -> QRect:
    """get current screen geometry"""
    screen = getCurrentScreen() or QApplication.primaryScreen()

    # this should not happen
    if not screen:
        return QRect(0, 0, 1920, 1080)

    return screen.availableGeometry() if available else screen.geometry()
