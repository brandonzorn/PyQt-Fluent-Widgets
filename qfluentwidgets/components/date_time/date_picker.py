from enum import Enum
from typing import List, Optional

from PyQt5.QtCore import pyqtProperty, pyqtSignal, QCalendar, QDate, Qt
from PyQt5.QtWidgets import QWidget

from .picker_base import DigitFormatter, PickerBase, PickerColumnFormatter, PickerPanel


class DatePickerBase(PickerBase):
    """Date picker base class"""

    dateChanged = pyqtSignal(QDate)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._date = QDate()
        self.calendar = QCalendar()
        self._yearFormatter = None
        self._monthFormatter = None
        self._dayFormatter = None

    def getDate(self) -> QDate:
        return self._date

    def setDate(self, date: QDate) -> None:
        """set current date"""
        raise NotImplementedError

    def setYearFormatter(self, formatter: PickerColumnFormatter) -> None:
        self._yearFormatter = formatter

    def setMonthFormatter(self, formatter: PickerColumnFormatter) -> None:
        self._monthFormatter = formatter

    def setDayFormatter(self, formatter: PickerColumnFormatter) -> None:
        self._dayFormatter = formatter

    def yearFormatter(self) -> PickerColumnFormatter:
        return self._yearFormatter or DigitFormatter()

    def dayFormatter(self) -> PickerColumnFormatter:
        return self._dayFormatter or DigitFormatter()

    def monthFormatter(self) -> PickerColumnFormatter:
        return self._monthFormatter or MonthFormatter()

    def reset(self) -> None:
        """Reset date"""
        self._date = QDate()
        super().reset()


class MonthFormatter(PickerColumnFormatter):
    """Month formatter"""

    def __init__(self) -> None:
        super().__init__()
        self.months = [
            self.tr("January"),
            self.tr("February"),
            self.tr("March"),
            self.tr("April"),
            self.tr("May"),
            self.tr("June"),
            self.tr("July"),
            self.tr("August"),
            self.tr("September"),
            self.tr("October"),
            self.tr("November"),
            self.tr("December"),
        ]

    def encode(self, month: int) -> str:
        return self.months[int(month) - 1]

    def decode(self, value: str) -> int:
        return self.months.index(value) + 1


class DatePicker(DatePickerBase):
    """Date picker"""

    class DateFormat(Enum):
        MM_DD_YYYY = 0
        YYYY_MM_DD = 1

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        dateFormat: DateFormat = DateFormat.MM_DD_YYYY,
        isMonthTight: bool = True,
    ) -> None:
        """
        Parameters
        ----------
        parent: Optional[QWidget]
            parent widget

        dateFormat: DatePickerFormat
            the format of date`

        isMonthTight: bool
            is the month column tight
        """
        super().__init__(parent=parent)
        self.MONTH = self.tr("month")
        self.YEAR = self.tr("year")
        self.DAY = self.tr("day")

        self.isMonthTight = isMonthTight
        self.setDateFormat(dateFormat)

    def setDateFormat(self, dateFormat: DateFormat) -> None:
        """set the format of date

        Parameters
        ----------
        dateFormat: DatePickerFormat
            the format of date`
        """
        self.clearColumns()
        y = QDate.currentDate().year()
        self.dateFormat = dateFormat

        if dateFormat == self.DateFormat.MM_DD_YYYY:
            self.monthIndex = 0
            self.dayIndex = 1
            self.yearIndex = 2

            self.addColumn(
                self.MONTH,
                range(1, 13),
                80,
                Qt.AlignmentFlag.AlignLeft,
                self.monthFormatter(),
            )
            self.addColumn(
                self.DAY,
                range(1, 32),
                80,
                formatter=self.dayFormatter(),
            )
            self.addColumn(
                self.YEAR,
                range(y - 100, y + 101),
                80,
                formatter=self.yearFormatter(),
            )
        elif dateFormat == self.DateFormat.YYYY_MM_DD:
            self.yearIndex = 0
            self.monthIndex = 1
            self.dayIndex = 2

            self.addColumn(
                self.YEAR,
                range(y - 100, y + 101),
                80,
                formatter=self.yearFormatter(),
            )
            self.addColumn(
                self.MONTH,
                range(1, 13),
                80,
                formatter=self.monthFormatter(),
            )
            self.addColumn(
                self.DAY,
                range(1, 32),
                80,
                formatter=self.dayFormatter(),
            )

        self.setColumnWidth(self.monthIndex, self._monthColumnWidth())

    def panelInitialValue(self) -> List[int]:
        if any(self.value()):
            return self.value()

        date = QDate.currentDate()
        y = self.encodeValue(self.yearIndex, date.year())
        m = self.encodeValue(self.monthIndex, date.month())
        d = self.encodeValue(self.dayIndex, date.day())
        return [y, m, d] if self.dateFormat == self.DateFormat.YYYY_MM_DD else [m, d, y]

    def setMonthTight(self, isTight: bool) -> None:
        """set whether the month column is tight"""
        if self.isMonthTight == isTight:
            return

        self.isMonthTight = isTight
        self.setColumnWidth(self.monthIndex, self._monthColumnWidth())

    def _monthColumnWidth(self) -> int:
        fm = self.fontMetrics()
        wm = max(fm.width(i) for i in self.columns[self.monthIndex].items()) + 20

        # don't use tight layout for english
        if self.MONTH == "month":
            return wm + 49

        return max(80, wm) if self.isMonthTight else wm + 49

    def _onColumnValueChanged(self, panel: PickerPanel, index: int, value: str) -> None:
        if index == self.dayIndex:
            return

        # get days number in month
        month = self.decodeValue(self.monthIndex, panel.columnValue(self.monthIndex))
        year = self.decodeValue(self.yearIndex, panel.columnValue(self.yearIndex))
        days = self.calendar.daysInMonth(month, year)

        # update days
        c = panel.column(self.dayIndex)
        day = c.currentItem().text()
        self.setColumnItems(self.dayIndex, range(1, days + 1))

        c.setItems(self.columns[self.dayIndex].items())
        c.setSelectedItem(day)

    def _onConfirmed(self, value: list) -> None:
        year = self.decodeValue(self.yearIndex, value[self.yearIndex])
        month = self.decodeValue(self.monthIndex, value[self.monthIndex])
        day = self.decodeValue(self.dayIndex, value[self.dayIndex])

        date, od = QDate(year, month, day), self.date
        self.setDate(date)

        if od != date:
            self.dateChanged.emit(date)

    def getDate(self) -> QDate:
        return self._date

    def setDate(self, date: QDate) -> None:
        if not date.isValid() or date.isNull():
            return

        self._date = date
        self.setColumnValue(self.monthIndex, date.month())
        self.setColumnValue(self.dayIndex, date.day())
        self.setColumnValue(self.yearIndex, date.year())
        self.setColumnItems(self.dayIndex, range(1, date.daysInMonth() + 1))

    date = pyqtProperty(QDate, getDate, setDate)


class ZhFormatter(PickerColumnFormatter):
    """Chinese date formatter"""

    suffix = ""

    def encode(self, value: int) -> str:
        return str(value) + self.suffix

    def decode(self, value: str, /) -> int:
        return int(value[:-1])


class ZhYearFormatter(ZhFormatter):
    """Chinese year formatter"""

    suffix = "年"


class ZhMonthFormatter(ZhFormatter):
    """Chinese month formatter"""

    suffix = "月"


class ZhDayFormatter(ZhFormatter):
    """Chinese day formatter"""

    suffix = "日"


class ZhDatePicker(DatePicker):
    """Chinese date picker"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent, DatePicker.DateFormat.YYYY_MM_DD)
        self.MONTH = "月"
        self.YEAR = "年"
        self.DAY = "日"
        self.setDayFormatter(ZhDayFormatter())
        self.setYearFormatter(ZhYearFormatter())
        self.setMonthFormatter(ZhMonthFormatter())
        self.setDateFormat(self.DateFormat.YYYY_MM_DD)
