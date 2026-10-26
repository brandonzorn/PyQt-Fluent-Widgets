from typing import Optional

from PyQt5.QtCore import QRect, QRectF
from PyQt5.QtGui import QPainterPath, QShowEvent
from PyQt5.QtWidgets import QFrame, QWidget

from ..widgets.tool_tip import ToolTip, ToolTipFilter
from .acrylic_widget import AcrylicWidget


class AcrylicToolTipContainer(AcrylicWidget, QFrame):
    """Acrylic tool tip container"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.setProperty("transparent", True)

    def acrylicClipPath(self) -> QPainterPath:
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect().adjusted(1, 1, -1, -1)), 3, 3)
        return path


class AcrylicToolTip(ToolTip):
    """Acrylic tool tip"""

    def _createContainer(self):
        return AcrylicToolTipContainer(self)

    def showEvent(self, e: QShowEvent) -> None:
        pos = self.pos() + self.container.pos()
        self.container.acrylicBrush.grabImage(QRect(pos, self.container.size()))
        super().showEvent(e)


class AcrylicToolTipFilter(ToolTipFilter):
    """Acrylic tool tip filter"""

    def _createToolTip(self) -> ToolTip:
        return AcrylicToolTip(self.parent().toolTip(), self.parent().window())
