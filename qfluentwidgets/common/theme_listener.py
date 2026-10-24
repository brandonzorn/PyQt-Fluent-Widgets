import sys
from typing import Optional

import darkdetect
from PyQt5.QtCore import pyqtSignal, QObject, QThread

from .config import qconfig, Theme


class SystemThemeListener(QThread):
    """System theme listener"""

    systemThemeChanged = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)

    def run(self) -> None:
        if sys.platform == "win32":
            darkdetect.listener(self._onThemeChanged)
            return

        while not self.isInterruptionRequested():
            t = darkdetect.theme().lower()
            theme = Theme.DARK if t == "dark" else Theme.LIGHT
            if theme != qconfig.theme:
                self._onThemeChanged(t)
                self.msleep(2000)  # anti shake
            else:
                self.msleep(1000)

    def _onThemeChanged(self, theme: str) -> None:
        theme: Theme = Theme.DARK if theme.lower() == "dark" else Theme.LIGHT

        if qconfig.themeMode.value != Theme.AUTO or theme == qconfig.theme:
            return

        qconfig.theme = Theme.AUTO
        qconfig._cfg.themeChanged.emit(Theme.AUTO)
        self.systemThemeChanged.emit()
