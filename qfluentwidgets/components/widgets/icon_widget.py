from typing import Optional, Union

from PyQt5.QtCore import pyqtProperty
from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtWidgets import QWidget

from ...common.icon import drawIcon, FluentIconBase, toQIcon
from ...common.overload import singledispatchmethod


class IconWidget(QWidget):
    """Icon widget

    Constructors
    ------------
    * IconWidget(`parent`: QWidget = None)
    * IconWidget(`icon`: QIcon | str | FluentIconBase, `parent`: QWidget = None)
    """

    @singledispatchmethod
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setIcon(QIcon())

    @__init__.register
    def _(self, icon: FluentIconBase, parent: Optional[QWidget] = None) -> None:
        self.__init__(parent)
        self.setIcon(icon)

    @__init__.register
    def _(self, icon: QIcon, parent: Optional[QWidget] = None) -> None:
        self.__init__(parent)
        self.setIcon(icon)

    @__init__.register
    def _(self, icon: str, parent: Optional[QWidget] = None) -> None:
        self.__init__(parent)
        self.setIcon(icon)

    def getIcon(self) -> QIcon:
        return toQIcon(self._icon)

    def setIcon(self, icon: Union[str, QIcon, FluentIconBase]) -> None:
        self._icon = icon
        self.update()

    def paintEvent(self, e: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        drawIcon(self._icon, painter, self.rect())

    icon = pyqtProperty(QIcon, getIcon, setIcon)
