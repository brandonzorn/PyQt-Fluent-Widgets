from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class VBoxLayout(QVBoxLayout):
    """Vertical box layout"""

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.widgets = []

    def addWidgets(
        self,
        widgets: List[QWidget],
        stretch: int = 0,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop,
    ) -> None:
        """add widgets to layout"""
        for widget in widgets:
            self.addWidget(widget, stretch, alignment)

    def addWidget(
        self,
        widget: QWidget,
        stretch: int = 0,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop,
    ) -> None:
        """add widget to layout"""
        super().addWidget(widget, stretch, alignment)
        self.widgets.append(widget)
        widget.show()

    def removeWidget(self, widget: QWidget) -> None:
        """remove widget from layout but not delete it"""
        super().removeWidget(widget)
        self.widgets.remove(widget)

    def deleteWidget(self, widget: QWidget) -> None:
        """remove widget from layout and delete it"""
        self.removeWidget(widget)
        widget.hide()
        widget.deleteLater()

    def removeAllWidget(self) -> None:
        """remove all widgets from layout"""
        for widget in self.widgets:
            super().removeWidget(widget)

        self.widgets.clear()
