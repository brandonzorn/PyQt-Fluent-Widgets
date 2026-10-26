from typing import Optional

from PyQt5.QtCore import QEvent, QObject, QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QLayout, QLayoutItem, QWidget


class ExpandLayout(QLayout):
    """Expand layout"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.__items = []
        self.__widgets = []

    def addWidget(self, widget: QWidget) -> None:
        if widget in self.__widgets:
            return

        self.__widgets.append(widget)
        widget.installEventFilter(self)

    def addItem(self, item: QLayoutItem) -> None:
        self.__items.append(item)

    def count(self) -> int:
        return len(self.__items)

    def itemAt(self, index: int) -> Optional[QLayoutItem]:
        if 0 <= index < len(self.__items):
            return self.__items[index]

        return None

    def takeAt(self, index: int) -> Optional[QLayoutItem]:
        if 0 <= index < len(self.__items):
            self.__widgets.pop(index)
            return self.__items.pop(index)

        return None

    def expandingDirections(self) -> Qt.Orientation:
        return Qt.Orientation.Vertical

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        """get the minimal height according to width"""
        return self.__doLayout(QRect(0, 0, width, 0), False)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self.__doLayout(rect, True)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()

        for w in self.__widgets:
            size = size.expandedTo(w.minimumSize())

        m = self.contentsMargins()
        size += QSize(m.left() + m.right(), m.top() + m.bottom())

        return size

    def __doLayout(self, rect: QRect, move: bool) -> int:
        """adjust widgets position according to the window size"""
        margin = self.contentsMargins()
        x = rect.x() + margin.left()
        y = rect.y() + margin.top()
        width = rect.width() - margin.left() - margin.right()

        for i, w in enumerate(self.__widgets):
            if w.isHidden():
                continue

            y += (i > 0) * self.spacing()
            if move:
                w.setGeometry(QRect(QPoint(x, y), QSize(width, w.height())))

            y += w.height()

        return y - rect.y()

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        if obj in self.__widgets and e.type() == QEvent.Type.Resize:
            re = QResizeEvent(e)
            ds: QSize = re.size() - re.oldSize()
            if ds.height() != 0 and ds.width() == 0:
                w = self.parentWidget()
                w.resize(w.width(), w.height() + ds.height())

        return super().eventFilter(obj, e)
