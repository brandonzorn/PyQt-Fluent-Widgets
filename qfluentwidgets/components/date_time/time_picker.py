from typing import List, Optional

from PyQt5.QtCore import pyqtProperty, pyqtSignal, QTime
from PyQt5.QtWidgets import QWidget

from .picker_base import DigitFormatter, PickerBase, PickerColumnFormatter


class TimePickerBase(PickerBase):
    """Time picker base class"""

    timeChanged = pyqtSignal(QTime)

    def __init__(self, parent: Optional[QWidget] = None, showSeconds: bool = False) -> None:
        super().__init__(parent=parent)
        self._isSecondVisible = showSeconds
        self._time = QTime()

    def getTime(self) -> QTime:
        return self._time

    def setTime(self, time: QTime) -> None:
        """set current time

        Parameters
        ----------
        time: QTime
            current time
        """
        raise NotImplementedError

    def isSecondVisible(self) -> bool:
        return self._isSecondVisible

    def setSecondVisible(self, isVisible: bool) -> None:
        """set the visibility of seconds column"""
        raise NotImplementedError

    def reset(self) -> None:
        """Reset time"""
        self._time = QTime()
        super().reset()


class MinuteFormatter(DigitFormatter):
    """Minute formatter"""

    def encode(self, minute, /):
        return str(minute).zfill(2)


class AMHourFormatter(DigitFormatter):
    """AM/PM Hour formatter"""

    def encode(self, hour, /):
        hour = int(hour)
        if hour in [0, 12]:
            return "12"

        return str(hour % 12)


class AMPMFormatter(PickerColumnFormatter):
    """AM/PM formatter"""

    def __init__(self) -> None:
        super().__init__()
        self.AM = self.tr("AM")
        self.PM = self.tr("PM")

    def encode(self, hour, /) -> str:
        if not str(hour).isdigit():
            return str(hour)

        hour = int(hour)
        return self.AM if hour < 12 else self.PM


class TimePicker(TimePickerBase):
    """24 hours time picker"""

    def __init__(self, parent: Optional[QWidget] = None, showSeconds: bool = False) -> None:
        super().__init__(parent, showSeconds)
        # add hour column
        w = 80 if showSeconds else 120
        self.addColumn(
            self.tr("hour"),
            range(24),
            w,
            formatter=DigitFormatter(),
        )

        # add minute column
        self.addColumn(
            self.tr("minute"),
            range(60),
            w,
            formatter=MinuteFormatter(),
        )

        # add seconds column
        self.addColumn(
            self.tr("second"),
            range(60),
            w,
            formatter=MinuteFormatter(),
        )
        self.setColumnVisible(2, showSeconds)

    def setTime(self, time: QTime) -> None:
        if not time.isValid() or time.isNull():
            return

        self._time = time
        self.setColumnValue(0, time.hour())
        self.setColumnValue(1, time.minute())
        self.setColumnValue(2, time.second())

    def setSecondVisible(self, isVisible: bool) -> None:
        self._isSecondVisible = isVisible
        self.setColumnVisible(2, isVisible)

        w = 80 if isVisible else 120
        for button in self.columns:
            button.setFixedWidth(w)

    def _onConfirmed(self, value: list) -> None:
        super()._onConfirmed(value)
        h = self.decodeValue(0, value[0])
        m = self.decodeValue(1, value[1])
        s = 0 if len(value) == 2 else self.decodeValue(2, value[2])

        time = QTime(h, m, s)
        ot = self.time
        self.setTime(time)

        if ot != time:
            self.timeChanged.emit(time)

    def panelInitialValue(self) -> List:
        if any(self.value()):
            return self.value()

        time = QTime.currentTime()
        h = self.encodeValue(0, time.hour())
        m = self.encodeValue(1, time.minute())
        s = self.encodeValue(2, time.second())
        return [h, m, s] if self.isSecondVisible() else [h, m]

    def getTime(self) -> QTime:
        return self._time

    def isSecondVisible(self) -> bool:
        return self._isSecondVisible

    time = pyqtProperty(QTime, getTime, setTime)
    secondVisible = pyqtProperty(bool, isSecondVisible, setSecondVisible)


class AMTimePicker(TimePickerBase):
    """AM/PM time picker"""

    def __init__(self, parent: Optional[QWidget] = None, showSeconds: bool = False) -> None:
        super().__init__(parent, showSeconds)
        self.AM = self.tr("AM")
        self.PM = self.tr("PM")

        # add hour column
        self.addColumn(
            self.tr("hour"),
            range(1, 13),
            80,
            formatter=AMHourFormatter(),
        )

        # add minute column
        self.addColumn(
            self.tr("minute"),
            range(60),
            80,
            formatter=MinuteFormatter(),
        )

        # add second column
        self.addColumn(
            self.tr("second"),
            range(60),
            80,
            formatter=MinuteFormatter(),
        )
        self.setColumnVisible(2, showSeconds)

        # add AM/PM column
        self.addColumn(self.AM, [self.AM, self.PM], 80, formatter=AMPMFormatter())

    def setSecondVisible(self, isVisible: bool) -> None:
        self._isSecondVisible = isVisible
        self.setColumnVisible(2, isVisible)

    def setTime(self, time: QTime) -> None:
        if not time.isValid() or time.isNull():
            return

        self._time = time
        self.setColumnValue(0, time.hour())
        self.setColumnValue(1, time.minute())
        self.setColumnValue(2, time.second())
        self.setColumnValue(3, time.hour())

    def _onConfirmed(self, value: list) -> None:
        super()._onConfirmed(value)

        if len(value) == 3:
            h, m, p = value
            s = 0
        else:
            h, m, s, p = value
            s = self.decodeValue(2, s)

        h = self.decodeValue(0, h)
        m = self.decodeValue(1, m)

        if p == self.AM:
            h = 0 if h == 12 else h
        elif p == self.PM:
            h = h if h == 12 else h + 12

        time = QTime(h, m, s)
        ot = self.time
        self.setTime(time)

        if ot != time:
            self.timeChanged.emit(time)

    def panelInitialValue(self) -> List:
        if any(self.value()):
            return self.value()

        time = QTime.currentTime()
        h = self.encodeValue(0, time.hour())
        m = self.encodeValue(1, time.minute())
        s = self.encodeValue(2, time.second())
        p = self.encodeValue(3, time.hour())
        return [h, m, s, p] if self.isSecondVisible() else [h, m, p]

    def getTime(self) -> QTime:
        return self._time

    def isSecondVisible(self) -> bool:
        return self._isSecondVisible

    time = pyqtProperty(QTime, getTime, setTime)
    secondVisible = pyqtProperty(bool, isSecondVisible, setSecondVisible)
