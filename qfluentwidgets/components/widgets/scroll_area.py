from typing import Optional

from PyQt5.QtCore import QEasingCurve, Qt
from PyQt5.QtGui import QKeyEvent, QWheelEvent
from PyQt5.QtWidgets import QScrollArea, QWidget

from ...common.smooth_scroll import SmoothMode, SmoothScroll
from .scroll_bar import SmoothScrollBar, SmoothScrollDelegate


class ScrollArea(QScrollArea):
    """Smooth scroll area"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.scrollDelegate = SmoothScrollDelegate(self)

    def setSmoothMode(self, mode: SmoothMode, orientation: Qt.Orientation) -> None:
        """set smooth mode

        Parameters
        ----------
        mode: SmoothMode
            smooth scroll mode

        orientation: Qt.Orientation
            scroll direction
        """
        if orientation == Qt.Orientation.Vertical:
            self.scrollDelegate.verticalSmoothScroll.setSmoothMode(mode)
        else:
            self.scrollDelegate.horizonSmoothScroll.setSmoothMode(mode)

    def enableTransparentBackground(self) -> None:
        self.setStyleSheet("QScrollArea{border: none; background: transparent}")

        if self.widget():
            self.widget().setStyleSheet("QWidget{background: transparent}")


class SingleDirectionScrollArea(QScrollArea):
    """Single direction scroll area"""

    def __init__(self, parent: Optional[QWidget] = None, orient: Qt.Orientation = Qt.Orientation.Vertical) -> None:
        """
        Parameters
        ----------
        parent: Optional[QWidget]
            parent widget

        orient: Qt.Orientation
            scroll orientation
        """
        super().__init__(parent)
        self.orient = orient
        self.smoothScroll = SmoothScroll(self, orient)
        self.vScrollBar = SmoothScrollBar(Qt.Orientation.Vertical, self)
        self.hScrollBar = SmoothScrollBar(Qt.Orientation.Horizontal, self)

    def setVerticalScrollBarPolicy(self, policy: Qt.ScrollBarPolicy) -> None:
        super().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.vScrollBar.setForceHidden(policy == Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def setHorizontalScrollBarPolicy(self, policy: Qt.ScrollBarPolicy) -> None:
        super().setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.hScrollBar.setForceHidden(policy == Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def setSmoothMode(self, mode: SmoothMode) -> None:
        """set smooth mode

        Parameters
        ----------
        mode: SmoothMode
            smooth scroll mode
        """
        self.smoothScroll.setSmoothMode(mode)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() in [Qt.Key.Key_Left, Qt.Key.Key_Right]:
            return

        super().keyPressEvent(e)

    def wheelEvent(self, e: QWheelEvent) -> None:
        if e.angleDelta().x() != 0:
            return

        self.smoothScroll.wheelEvent(e)
        e.setAccepted(True)

    def enableTransparentBackground(self) -> None:
        self.setStyleSheet("QScrollArea{border: none; background: transparent}")

        if self.widget():
            self.widget().setStyleSheet("QWidget{background: transparent}")


class SmoothScrollArea(QScrollArea):
    """Smooth scroll area"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.delegate = SmoothScrollDelegate(self, True)

    def setScrollAnimation(
        self,
        orient: Qt.Orientation,
        duration: int,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    ) -> None:
        """set scroll animation

        Parameters
        ----------
        orient: Qt.Orientation
            scroll orientation

        duration: int
            scroll duration

        easing: QEasingCurve.Type
            animation type
        """
        bar = self.delegate.hScrollBar if orient == Qt.Orientation.Horizontal else self.delegate.vScrollBar
        bar.setScrollAnimation(duration, easing)

    def enableTransparentBackground(self) -> None:
        self.setStyleSheet("QScrollArea{border: none; background: transparent}")

        if self.widget():
            self.widget().setStyleSheet("QWidget{background: transparent}")
