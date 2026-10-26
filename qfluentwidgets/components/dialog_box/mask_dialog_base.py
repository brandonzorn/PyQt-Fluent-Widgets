from typing import Optional

from PyQt5.QtCore import QEasingCurve, QEvent, QObject, QPoint, QPropertyAnimation, Qt
from PyQt5.QtGui import QColor, QResizeEvent, QShowEvent
from PyQt5.QtWidgets import QDialog, QFrame, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QHBoxLayout, QWidget

from ...common.config import isDarkTheme


class MaskDialogBase(QDialog):
    """Dialog box base class with a mask"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self._isClosableOnMaskClicked = False
        self._isDraggable = False
        self._dragPos = QPoint()
        self._hBoxLayout = QHBoxLayout(self)
        self.windowMask = QWidget(self)

        # dialog box in the center of mask, all widgets take it as parent
        self.widget = QFrame(self, objectName="centerWidget")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, parent.width(), parent.height())

        c = 0 if isDarkTheme() else 255
        self.windowMask.resize(self.size())
        self.windowMask.setStyleSheet(f"background:rgba({c}, {c}, {c}, 0.6)")
        self._hBoxLayout.addWidget(self.widget)
        self.setShadowEffect()

        self.window().installEventFilter(self)
        self.windowMask.installEventFilter(self)
        self.widget.installEventFilter(self)

    def setShadowEffect(
        self,
        blurRadius: int = 60,
        offset: tuple[int, int] = (0, 10),
        color: QColor = QColor(0, 0, 0, 100),
    ) -> None:
        """add shadow to dialog"""
        shadowEffect = QGraphicsDropShadowEffect(self.widget)
        shadowEffect.setBlurRadius(blurRadius)
        shadowEffect.setOffset(*offset)
        shadowEffect.setColor(color)
        self.widget.setGraphicsEffect(None)
        self.widget.setGraphicsEffect(shadowEffect)

    def setMaskColor(self, color: QColor) -> None:
        """set the color of mask"""
        self.windowMask.setStyleSheet(f"""
            background: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})
        """)

    def showEvent(self, e: QShowEvent) -> None:
        """fade in"""
        opacityEffect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacityEffect)
        opacityAni = QPropertyAnimation(opacityEffect, b"opacity", self)
        opacityAni.setStartValue(0)
        opacityAni.setEndValue(1)
        opacityAni.setDuration(200)
        opacityAni.setEasingCurve(QEasingCurve.InSine)
        opacityAni.finished.connect(lambda: self.setGraphicsEffect(None))
        opacityAni.start()
        super().showEvent(e)

    def done(self, code: int) -> None:
        """fade out"""
        self.widget.setGraphicsEffect(None)
        opacityEffect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacityEffect)
        opacityAni = QPropertyAnimation(opacityEffect, b"opacity", self)
        opacityAni.setStartValue(1)
        opacityAni.setEndValue(0)
        opacityAni.setDuration(100)
        opacityAni.finished.connect(lambda: self._onDone(code))
        opacityAni.start()

    def _onDone(self, code: int) -> None:
        self.setGraphicsEffect(None)
        QDialog.done(self, code)

    def isClosableOnMaskClicked(self) -> bool:
        return self._isClosableOnMaskClicked

    def setClosableOnMaskClicked(self, isClosable: bool) -> None:
        self._isClosableOnMaskClicked = isClosable

    def setDraggable(self, draggable: bool) -> None:
        self._isDraggable = draggable

    def isDraggable(self) -> bool:
        return self._isDraggable

    def resizeEvent(self, e: QResizeEvent) -> None:
        self.windowMask.resize(self.size())

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        if obj is self.window():
            if e.type() == QEvent.Type.Resize:
                re = QResizeEvent(e)
                self.resize(re.size())
        elif obj is self.windowMask:
            if (
                e.type() == QEvent.Type.MouseButtonRelease
                and e.button() == Qt.MouseButton.LeftButton
                and self.isClosableOnMaskClicked()
            ):
                self.reject()
        elif obj is self.widget and self.isDraggable():
            if e.type() == QEvent.Type.MouseButtonPress and e.button() == Qt.MouseButton.LeftButton:
                if not self.widget.childrenRegion().contains(e.pos()):
                    self._dragPos = e.pos()
                    return True
            elif e.type() == QEvent.Type.MouseMove and not self._dragPos.isNull():
                pos = self.widget.pos() + e.pos() - self._dragPos
                pos.setX(max(0, min(pos.x(), self.width() - self.widget.width())))
                pos.setY(max(0, min(pos.y(), self.height() - self.widget.height())))

                self.widget.move(pos)
                return True
            elif e.type() == QEvent.Type.MouseButtonRelease:
                self._dragPos = QPoint()

        return super().eventFilter(obj, e)
