from typing import Callable, Optional, Union

from PyQt5.QtCore import pyqtSignal, QRectF, Qt
from PyQt5.QtGui import QColor, QIcon, QPainter, QPaintEvent
from PyQt5.QtWidgets import QApplication, QWidget

from ...common.animation import FluentAnimation, FluentAnimationProperty, FluentAnimationType
from ...common.color import autoFallbackThemeColor
from ...common.font import setFont
from ...common.icon import drawIcon, FluentIconBase, Theme
from ...common.style_sheet import FluentStyleSheet, isDarkTheme
from ..widgets.button import ToolButton, TransparentToolButton
from .pivot import Pivot, PivotItem


class SegmentedItem(PivotItem):
    """Segmented item"""

    def _postInit(self) -> None:
        super()._postInit()
        setFont(self, 14)


class SegmentedToolItem(ToolButton):
    """Pivot item"""

    itemClicked = pyqtSignal(bool)

    def _postInit(self) -> None:
        self.isSelected = False
        self.setProperty("isSelected", False)
        self.clicked.connect(lambda: self.itemClicked.emit(True))

        self.setFixedSize(38, 33)
        FluentStyleSheet.PIVOT.apply(self)

    def setSelected(self, isSelected: bool) -> None:
        if self.isSelected == isSelected:
            return

        self.isSelected = isSelected
        self.setProperty("isSelected", isSelected)
        self.setStyle(QApplication.style())
        self.update()


class SegmentedToggleToolItem(TransparentToolButton):
    itemClicked = pyqtSignal(bool)

    def _postInit(self) -> None:
        super()._postInit()
        self.isSelected = False

        self.setFixedSize(50, 32)
        self.clicked.connect(lambda: self.itemClicked.emit(True))

    def setSelected(self, isSelected: bool) -> None:
        if self.isSelected == isSelected:
            return

        self.isSelected = isSelected
        self.setChecked(isSelected)

    def _drawIcon(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        painter: QPainter,
        rect: QRectF,
        state: QIcon.State = QIcon.State.Off,
    ) -> None:
        if self.isSelected and isinstance(icon, FluentIconBase):
            theme = Theme.DARK if not isDarkTheme() else Theme.LIGHT
            icon = icon.icon(theme)

        drawIcon(icon, painter, rect, state)


class SegmentedWidget(Pivot):
    """Segmented widget"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.slideAni = FluentAnimation.create(
            FluentAnimationType.POINT_TO_POINT,
            FluentAnimationProperty.SCALE,
            value=0,
            parent=self,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

    def insertItem(
        self,
        index: int,
        routeKey: str,
        text: str,
        onClick: Optional[Callable] = None,
        icon: Optional[Union[str, QIcon, FluentIconBase]] = None,
    ) -> Optional[SegmentedItem]:
        if routeKey in self.items:
            return None

        item = SegmentedItem(text, self)
        if icon:
            item.setIcon(icon)

        self.insertWidget(index, routeKey, item, onClick)
        return item

    def paintEvent(self, e: QPaintEvent) -> None:
        QWidget.paintEvent(self, e)

        if not self.currentItem():
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        # draw background
        if isDarkTheme():
            painter.setPen(QColor(255, 255, 255, 14))
            painter.setBrush(QColor(255, 255, 255, 15))
        else:
            painter.setPen(QColor(0, 0, 0, 19))
            painter.setBrush(QColor(255, 255, 255, 179))

        item = self.currentItem()
        rect = item.rect().adjusted(1, 1, -1, -1).translated(int(self.slideAni.value()), 0)
        painter.drawRoundedRect(rect, 5, 5)

        # draw indicator
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(autoFallbackThemeColor(self.lightIndicatorColor, self.darkIndicatorColor))

        x = int(self.currentItem().width() / 2 - 8 + self.slideAni.value())
        painter.drawRoundedRect(QRectF(x, self.height() - 3.5, 16, 3), 1.5, 1.5)

    def currentIndicatorGeometry(self) -> int:
        return self.currentItem().x() if self.currentItem() else 0


class SegmentedToolWidget(SegmentedWidget):
    """Segmented tool widget"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

    def addItem(
        self,
        routeKey: str,
        icon: Union[str, QIcon, FluentIconBase],
        onClick: Optional[Callable] = None,
    ):
        """add item

        Parameters
        ----------
        routeKey: str
            the unique name of item

        icon: str | QIcon | FluentIconBase
            the icon of navigation item

        onClick: callable
            the slot connected to item clicked signal
        """
        return self.insertItem(-1, routeKey, icon, onClick)

    def insertItem(
        self,
        index: int,
        routeKey: str,
        icon: Union[str, QIcon, FluentIconBase],
        onClick: Optional[Callable] = None,
    ):
        if routeKey in self.items:
            return None

        item = self._createItem(icon)
        self.insertWidget(index, routeKey, item, onClick)
        return item

    def _createItem(self, icon: Union[str, QIcon, FluentIconBase]) -> SegmentedToolItem:
        return SegmentedToolItem(icon)


class SegmentedToggleToolWidget(SegmentedToolWidget):
    """Segmented toggle tool widget"""

    def _createItem(self, icon: Union[str, QIcon, FluentIconBase]) -> SegmentedToggleToolItem:
        return SegmentedToggleToolItem(icon)

    def paintEvent(self, e: QPaintEvent) -> None:
        QWidget.paintEvent(self, e)

        if not self.currentItem():
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(autoFallbackThemeColor(self.lightIndicatorColor, self.darkIndicatorColor))

        item = self.currentItem()
        painter.drawRoundedRect(QRectF(self.slideAni.value(), 0, item.width(), item.height()), 4, 4)
