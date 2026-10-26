from typing import Optional

from PyQt5.QtCore import QEvent, QSizeF, Qt, QTimer, QUrl
from PyQt5.QtGui import QHideEvent, QPainter, QResizeEvent, QShowEvent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QStyleOptionGraphicsItem, QVBoxLayout, QWidget

from ..common.style_sheet import FluentStyleSheet
from .media_play_bar import StandardMediaPlayBar


class GraphicsVideoItem(QGraphicsVideoItem):
    """Graphics video item"""

    def paint(
        self,
        painter: Optional[QPainter],
        option: Optional[QStyleOptionGraphicsItem],
        widget: Optional[QWidget] = None,
    ) -> None:
        painter.setCompositionMode(QPainter.CompositionMode_Difference)
        super().paint(painter, option, widget)


class VideoWidget(QGraphicsView):
    """Video widget"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.isHover = False
        self.timer = QTimer(self)

        self.vBoxLayout = QVBoxLayout(self)
        self.videoItem = QGraphicsVideoItem()
        self.graphicsScene = QGraphicsScene(self)
        self.playBar = StandardMediaPlayBar(self)

        self.setMouseTracking(True)
        self.setScene(self.graphicsScene)
        self.graphicsScene.addItem(self.videoItem)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        self.player.setVideoOutput(self.videoItem)
        FluentStyleSheet.MEDIA_PLAYER.apply(self)

        self.timer.timeout.connect(self._onHideTimeOut)

    def setVideo(self, url: QUrl) -> None:
        """set the video to play"""
        self.player.setSource(url)
        self.fitInView(self.videoItem, Qt.AspectRatioMode.KeepAspectRatio)

    def hideEvent(self, e: QHideEvent) -> None:
        self.pause()
        e.accept()

    def wheelEvent(self, e: QShowEvent) -> None:
        return

    def enterEvent(self, e: QEvent) -> None:
        self.isHover = True
        self.playBar.fadeIn()

    def leaveEvent(self, e: QEvent) -> None:
        self.isHover = False
        self.timer.start(3000)

    def _onHideTimeOut(self) -> None:
        if not self.isHover:
            self.playBar.fadeOut()

    def play(self) -> None:
        self.playBar.play()

    def pause(self) -> None:
        self.playBar.pause()

    def stop(self) -> None:
        self.playBar.stop()

    def togglePlayState(self) -> None:
        """toggle play state"""
        if self.player.isPlaying():
            self.pause()
        else:
            self.play()

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        self.videoItem.setSize(QSizeF(self.size()))
        self.fitInView(self.videoItem, Qt.AspectRatioMode.KeepAspectRatio)
        self.playBar.move(11, self.height() - self.playBar.height() - 11)
        self.playBar.setFixedSize(self.width() - 22, self.playBar.height())

    @property
    def player(self):
        return self.playBar.player
