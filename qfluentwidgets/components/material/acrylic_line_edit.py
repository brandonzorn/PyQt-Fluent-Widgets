from PyQt5.QtWidgets import QCompleter

from ..widgets.line_edit import LineEdit, SearchLineEdit
from .acrylic_menu import AcrylicCompleterMenu, AcrylicLineEditMenu


class AcrylicLineEditBase:
    """Acrylic line edit base"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def setCompleter(self, completer: QCompleter) -> None:
        super().setCompleter(completer)
        self.setCompleterMenu(AcrylicCompleterMenu(self))

    def contextMenuEvent(self, e) -> None:
        menu = AcrylicLineEditMenu(self)
        menu.exec(e.globalPos())


class AcrylicLineEdit(AcrylicLineEditBase, LineEdit):
    """Acrylic line edit"""


class AcrylicSearchLineEdit(AcrylicLineEditBase, SearchLineEdit):
    """Acrylic search line edit"""
