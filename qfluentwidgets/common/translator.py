from typing import Optional

from PyQt5.QtCore import QLocale, QObject, QTranslator


class FluentTranslator(QTranslator):
    """Translator of fluent widgets"""

    def __init__(self, locale: Optional[QLocale] = None, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.load(locale or QLocale())

    def load(self, locale: QLocale) -> bool:
        """load translation file"""
        return super().load(f":/qfluentwidgets/i18n/qfluentwidgets.{locale.name()}.qm")
