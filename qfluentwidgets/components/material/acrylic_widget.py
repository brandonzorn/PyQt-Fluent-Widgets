from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPaintEvent

from ...common.style_sheet import isDarkTheme
from ..widgets.acrylic_label import AcrylicBrush


class AcrylicWidget:
    """Acrylic widget"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.acrylicBrush = AcrylicBrush(self, 30)

    def _updateAcrylicColor(self) -> None:
        if isDarkTheme():
            tintColor = QColor(32, 32, 32, 200)
            luminosityColor = QColor(0, 0, 0, 0)
        else:
            tintColor = QColor(255, 255, 255, 180)
            luminosityColor = QColor(255, 255, 255, 0)

        self.acrylicBrush.tintColor = tintColor
        self.acrylicBrush.luminosityColor = luminosityColor

    def acrylicClipPath(self) -> QPainterPath:
        return QPainterPath()

    def _drawAcrylic(self, painter: QPainter) -> None:
        path = self.acrylicClipPath()
        if not path.isEmpty():
            self.acrylicBrush.clipPath = self.acrylicClipPath()

        self._updateAcrylicColor()
        self.acrylicBrush.paint()

    def paintEvent(self, e: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        self._drawAcrylic(painter)
        super().paintEvent(e)
