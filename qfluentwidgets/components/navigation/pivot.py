from typing import Callable, Dict, Optional, Union

from PyQt5.QtCore import pyqtSignal, QRectF, Qt
from PyQt5.QtGui import QColor, QIcon, QPainter, QPaintEvent, QResizeEvent, QShowEvent
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QSizePolicy, QWidget

from ...common.animation import ScaleSlideAnimation
from ...common.color import autoFallbackThemeColor
from ...common.font import setFont
from ...common.icon import FluentIconBase
from ...common.router import qrouter
from ...common.style_sheet import FluentStyleSheet
from ..widgets.button import PushButton
from .navigation_panel import RouteKeyError


class PivotItem(PushButton):
    """Pivot item"""

    itemClicked = pyqtSignal(bool)

    def _postInit(self) -> None:
        self.isSelected = False
        self.setProperty("isSelected", False)
        self.clicked.connect(lambda: self.itemClicked.emit(True))
        self.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)

        FluentStyleSheet.PIVOT.apply(self)
        setFont(self, 18)

    def setSelected(self, isSelected: bool) -> None:
        if self.isSelected == isSelected:
            return

        self.isSelected = isSelected
        self.setProperty("isSelected", isSelected)
        self.setStyle(QApplication.style())
        self.update()


class Pivot(QWidget):
    """Pivot"""

    currentItemChanged = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.items: Dict[str, PivotItem] = {}
        self._currentRouteKey = None
        self._indicatorLength = 16

        self.lightIndicatorColor = QColor()
        self.darkIndicatorColor = QColor()

        self.hBoxLayout = QHBoxLayout(self)
        self.slideAni = ScaleSlideAnimation(self)

        FluentStyleSheet.PIVOT.apply(self)

        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.slideAni.valueChanged.connect(self.update)

    def addItem(
        self,
        routeKey: str,
        text: str,
        onClick: Optional[Callable] = None,
        icon: Optional[Union[str, QIcon, FluentIconBase]] = None,
    ) -> Optional[PivotItem]:
        """add item

        Parameters
        ----------
        routeKey: str
            the unique name of item

        text: str
            the text of navigation item

        onClick: callable
            the slot connected to item clicked signal

        icon: str
            the icon of navigation item
        """
        return self.insertItem(-1, routeKey, text, onClick, icon)

    def addWidget(self, routeKey: str, widget: PivotItem, onClick: Optional[Callable] = None) -> None:
        """add widget

        Parameters
        ----------
        routeKey: str
            the unique name of item

        widget: PivotItem
            navigation widget

        onClick: callable
            the slot connected to item clicked signal
        """
        self.insertWidget(-1, routeKey, widget, onClick)

    def insertItem(
        self,
        index: int,
        routeKey: str,
        text: str,
        onClick: Optional[Callable] = None,
        icon: Optional[Union[str, QIcon, FluentIconBase]] = None,
    ) -> Optional[PivotItem]:
        """insert item

        Parameters
        ----------
        index: int
            insert position

        routeKey: str
            the unique name of item

        text: str
            the text of navigation item

        onClick: callable
            the slot connected to item clicked signal

        icon: Optional[Union[str, QIcon, FluentIconBase]]
            the icon of navigation item
        """
        if routeKey in self.items:
            return None

        item = PivotItem(text, self)
        if icon:
            item.setIcon(icon)

        self.insertWidget(index, routeKey, item, onClick)
        return item

    def insertWidget(self, index: int, routeKey: str, widget: PivotItem, onClick: Optional[Callable] = None) -> None:
        """insert item

        Parameters
        ----------
        index: int
            insert position

        routeKey: str
            the unique name of item

        widget: PivotItem
            navigation widget

        onClick: callable
            the slot connected to item clicked signal
        """
        if routeKey in self.items:
            return

        widget.setProperty("routeKey", routeKey)
        widget.itemClicked.connect(self._onItemClicked)
        if onClick:
            widget.itemClicked.connect(onClick)

        self.items[routeKey] = widget
        self.hBoxLayout.insertWidget(index, widget, 1)

    def removeWidget(self, routeKey: str) -> None:
        """remove widget

        Parameters
        ----------
        routeKey: str
            the unique name of item
        """
        if routeKey not in self.items:
            return

        item = self.items.pop(routeKey)
        self.hBoxLayout.removeWidget(item)
        qrouter.remove(routeKey)
        item.deleteLater()

        if not self.items:
            self._currentRouteKey = None

    def clear(self) -> None:
        """clear all navigation items"""
        for k, w in self.items.items():
            self.hBoxLayout.removeWidget(w)
            qrouter.remove(k)
            w.deleteLater()

        self.items.clear()
        self._currentRouteKey = None

    def currentItem(self) -> Optional[PivotItem]:
        """Returns the current selected item"""
        if self._currentRouteKey is None:
            return None

        return self.widget(self._currentRouteKey)

    def currentRouteKey(self) -> str:
        return self._currentRouteKey

    def setCurrentItem(self, routeKey: str) -> None:
        """set current selected item

        Parameters
        ----------
        routeKey: str
            the unique name of item
        """
        if routeKey not in self.items or routeKey == self.currentRouteKey():
            return

        self._adjustIndicatorPos()

        self._currentRouteKey = routeKey
        self.slideAni.startAnimation(self.currentIndicatorGeometry())

        for k, item in self.items.items():
            item.setSelected(k == routeKey)

        self.currentItemChanged.emit(routeKey)

    def showEvent(self, e: QShowEvent) -> None:
        super().showEvent(e)
        self._adjustIndicatorPos()

    def setIndicatorLength(self, value: int) -> None:
        self._indicatorLength = value
        self._adjustIndicatorPos()

    def indicatorLength(self) -> int:
        return self._indicatorLength

    def setItemFontSize(self, size: int) -> None:
        """set the pixel font size of items"""
        for item in self.items.values():
            font = item.font()
            font.setPixelSize(size)
            item.setFont(font)
            item.adjustSize()

    def setItemText(self, routeKey: str, text: str) -> None:
        """set the text of item"""
        item = self.widget(routeKey)
        item.setText(text)

    def setIndicatorColor(self, light: QColor, dark: QColor) -> None:
        self.lightIndicatorColor = QColor(light)
        self.darkIndicatorColor = QColor(dark)
        self.update()

    def _onItemClicked(self) -> None:
        item: PivotItem = self.sender()
        self.setCurrentItem(item.property("routeKey"))

    def widget(self, routeKey: str) -> PivotItem:
        if routeKey not in self.items:
            msg = f"`{routeKey}` is illegal."
            raise RouteKeyError(msg)

        return self.items[routeKey]

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        self._adjustIndicatorPos()

    def _adjustIndicatorPos(self) -> None:
        item = self.currentItem()
        if item:
            self.slideAni.stop()
            self.slideAni.setValue(self.currentIndicatorGeometry())

    def currentIndicatorGeometry(self) -> QRectF:
        item = self.currentItem()
        if not item:
            return QRectF(0, self.height() - 3, self.indicatorLength(), 3)

        rect = item.geometry()
        return QRectF(
            rect.x() - self.indicatorLength() // 2 + rect.width() // 2,
            self.height() - 3,
            self.indicatorLength(),
            3,
        )

    def paintEvent(self, e: QPaintEvent) -> None:
        super().paintEvent(e)

        if not self.currentItem():
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(autoFallbackThemeColor(self.lightIndicatorColor, self.darkIndicatorColor))
        painter.drawRoundedRect(self.slideAni.geometry, 1.5, 1.5)
