from typing import List, Optional

from PyQt5.QtCore import QPoint, QRect, QRectF, QSize, Qt
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QShowEvent
from PyQt5.QtWidgets import QLineEdit, QListWidget, QListWidgetItem, QWidget

from ...common.style_sheet import isDarkTheme
from ..widgets.acrylic_label import AcrylicBrush
from ..widgets.line_edit import CompleterMenu, LineEdit
from ..widgets.menu import (
    CheckableMenu,
    IndicatorMenuItemDelegate,
    LineEditMenu,
    MenuActionListWidget,
    MenuAnimationManager,
    MenuAnimationType,
    MenuIndicatorType,
    RoundMenu,
)


class AcrylicMenuActionListWidget(MenuActionListWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.acrylicBrush = AcrylicBrush(self.viewport(), 35)
        self.setViewportMargins(0, 0, 0, 0)
        self.setProperty("transparent", True)

        super().addItem(self.createPlaceholderItem(self._topMargin()))
        super().addItem(self.createPlaceholderItem(self._bottomMargin()))

    def _updateAcrylicColor(self) -> None:
        if isDarkTheme():
            tintColor = QColor(32, 32, 32, 200)
            luminosityColor = QColor(0, 0, 0, 0)
        else:
            tintColor = QColor(255, 255, 255, 160)
            luminosityColor = QColor(255, 255, 255, 50)

        self.acrylicBrush.tintColor = tintColor
        self.acrylicBrush.luminosityColor = luminosityColor

    def _topMargin(self) -> int:
        return 6

    def _bottomMargin(self) -> int:
        return 6

    def setItemHeight(self, height: int) -> None:
        """set the height of item"""
        if height == self._itemHeight:
            return

        for i in range(1, self.count() - 1):
            item = self.item(i)
            if not self.itemWidget(item):
                item.setSizeHint(QSize(item.sizeHint().width(), height))

        self._itemHeight = height
        self.adjustSize()

    def addItem(self, item: QListWidgetItem) -> None:
        super().insertItem(self.count() - 1, item)

    def createPlaceholderItem(self, height: int = 2) -> QListWidgetItem:
        item = QListWidgetItem()
        item.setSizeHint(QSize(1, height))
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        return item

    def clipPath(self) -> QPainterPath:
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(self.rect()).adjusted(0, 0, -2.5, -2.5),
            8,
            8,
        )
        return path

    def paintEvent(self, e: QPaintEvent) -> None:
        painter = QPainter(self.viewport())
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        self.acrylicBrush.clipPath = self.clipPath()
        self._updateAcrylicColor()
        self.acrylicBrush.paint()

        super().paintEvent(e)


class AcrylicMenuBase:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def setUpMenu(self, view) -> None:
        self.hBoxLayout.removeWidget(self.view)
        self.view.deleteLater()

        self.view = view
        self.hBoxLayout.addWidget(self.view)

        self.setShadowEffect()

        self.view.itemClicked.connect(self._onItemClicked)
        self.view.itemEntered.connect(self._onItemEntered)

    def exec(self, pos: QPoint, ani: bool = True, aniType: MenuAnimationType = MenuAnimationType.DROP_DOWN) -> None:
        p = MenuAnimationManager.make(self, aniType)._endPosition(pos)
        self.view.acrylicBrush.grabImage(QRect(p, self.layout().sizeHint()))
        super().exec(pos, ani, aniType)


class AcrylicMenu(AcrylicMenuBase, RoundMenu):
    """Acrylic menu"""

    def __init__(self, title: str = "", parent=None) -> None:
        super().__init__(title, parent)
        self.setUpMenu(AcrylicMenuActionListWidget(self))


class AcrylicCompleterMenuActionListWidget(AcrylicMenuActionListWidget):
    def clipPath(self) -> QPainterPath:
        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        path.addRoundedRect(QRectF(self.rect()).adjusted(1, 1, -2.5, -2.5), 8, 8)

        if self.property("dropDown"):
            path.addRect(1, 1, 11, 11)
            path.addRect(self.width() - 12, 1, 11, 11)
        else:
            path.addRect(1, self.height() - 11, 11, 11)
            path.addRect(self.width() - 12, self.height() - 11, 11, 11)

        return path


class AcrylicCompleterMenu(AcrylicMenuBase, CompleterMenu):
    """Acrylic completer menu"""

    def __init__(self, lineEdit: LineEdit) -> None:
        super().__init__(lineEdit)
        self.setUpMenu(AcrylicCompleterMenuActionListWidget(self))

        self.view.setObjectName("completerListWidget")
        self.view.setItemDelegate(IndicatorMenuItemDelegate())
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setItemHeight(33)

    def _onItemClicked(self, item) -> None:
        self._hideMenu(False)
        self._onCompletionItemSelected(item.text(), self.view.row(item) - 1)

    def setItems(self, items: List[str]) -> None:
        """set completion items"""
        self.view.clear()

        self.items = items
        QListWidget.addItem(self.view, self.view.createPlaceholderItem(self.view._topMargin()))
        self.view.addItems(items)

        for i in range(1, self.view.count()):
            item = self.view.item(i)
            item.setSizeHint(QSize(1, self.itemHeight))

        QListWidget.addItem(self.view, self.view.createPlaceholderItem(self.view._bottomMargin()))


class AcrylicLineEditMenu(AcrylicMenuBase, LineEditMenu):
    """Acrylic line edit menu"""

    def __init__(self, parent: QLineEdit) -> None:
        super().__init__(parent)
        self.setUpMenu(AcrylicMenuActionListWidget(self))


class AcrylicCheckableMenu(AcrylicMenuBase, CheckableMenu):
    """Checkable menu"""

    def __init__(
        self,
        title: str = "",
        parent=None,
        indicatorType: MenuIndicatorType = MenuIndicatorType.CHECK,
    ) -> None:
        super().__init__(title, parent, indicatorType)
        self.setUpMenu(AcrylicMenuActionListWidget(self))
        self.view.setObjectName("checkableListWidget")


class AcrylicSystemTrayMenu(AcrylicMenu):
    """System tray menu"""

    def showEvent(self, e: QShowEvent) -> None:
        super().showEvent(e)
        self.adjustPosition()
        self.view.acrylicBrush.grabImage(QRect(self.pos(), self.layout().sizeHint()))


class AcrylicCheckableSystemTrayMenu(AcrylicCheckableMenu):
    """Checkable system tray menu"""

    def showEvent(self, e: QShowEvent) -> None:
        super().showEvent(e)
        self.adjustPosition()
