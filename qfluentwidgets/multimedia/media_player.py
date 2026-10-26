from typing import Optional

from PyQt5.QtCore import pyqtSignal, QObject, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer


class MediaPlayerBase(QObject):
    """Media player base class"""

    mediaStatusChanged = pyqtSignal(QMediaPlayer.MediaStatus)
    playbackRateChanged = pyqtSignal(float)
    positionChanged = pyqtSignal(int)
    durationChanged = pyqtSignal(int)
    sourceChanged = pyqtSignal(QUrl)
    volumeChanged = pyqtSignal(int)
    mutedChanged = pyqtSignal(bool)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)

    def isPlaying(self) -> bool:
        """Whether the media is playing"""
        raise NotImplementedError

    def mediaStatus(self) -> QMediaPlayer.MediaStatus:
        """Return the status of the current media stream"""
        raise NotImplementedError

    def playbackState(self) -> QMediaPlayer.State:
        """Return the playback status of the current media stream"""
        raise NotImplementedError

    def duration(self) -> int:
        """Returns the duration of the current media in ms"""
        raise NotImplementedError

    def position(self) -> int:
        """Returns the current position inside the media being played back in ms"""
        raise NotImplementedError

    def volume(self) -> int:
        """Return the volume of player"""
        raise NotImplementedError

    def source(self) -> QUrl:
        """Return the active media source being used"""
        raise NotImplementedError

    def pause(self) -> None:
        """Pause playing the current source"""
        raise NotImplementedError

    def play(self) -> None:
        """Start or resume playing the current source"""
        raise NotImplementedError

    def stop(self) -> None:
        """Stop playing, and reset the play position to the beginning"""
        raise NotImplementedError

    def playbackRate(self) -> float:
        """Return the playback rate of the current media"""
        raise NotImplementedError

    def setPosition(self, position: int) -> None:
        """Sets the position of media in ms"""
        raise NotImplementedError

    def setSource(self, media: QUrl) -> None:
        """Sets the current source"""
        raise NotImplementedError

    def setPlaybackRate(self, rate: float) -> None:
        """Sets the playback rate of player"""
        raise NotImplementedError

    def setVolume(self, volume: int) -> None:
        """Sets the volume of player"""
        raise NotImplementedError

    def setMuted(self, isMuted: bool) -> None:
        raise NotImplementedError

    def videoOutput(self) -> QObject:
        """Return the video output to be used by the media player"""
        raise NotImplementedError

    def setVideoOutput(self, output: QObject) -> None:
        """Sets the video output to be used by the media player"""
        raise NotImplementedError


class MediaPlayer(QMediaPlayer):
    """Media player"""

    sourceChanged = pyqtSignal(QUrl)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.mediaChanged.connect(lambda i: i.canonicalUrl())
        self.setNotifyInterval(1000)

    def isPlaying(self) -> bool:
        return self.state() == QMediaPlayer.State.PlayingState

    def source(self) -> QUrl:
        """Return the active media source being used"""
        return self.currentMedia().canonicalUrl()

    def setSource(self, media: QUrl) -> None:
        """Sets the current source"""
        self.setMedia(QMediaContent(media))
