from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QPolygonF
from PyQt6.QtCore import QPointF, QRectF
from app.constants import (
    SPARKLINE_WIDTH, SPARKLINE_HEIGHT,
    COLOR_SPARKLINE_UP, COLOR_SPARKLINE_DOWN,
)


class SparklineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._prices: list = []
        self._is_positive: bool = True
        self.setFixedSize(SPARKLINE_WIDTH, SPARKLINE_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_data(self, prices: list) -> None:
        self._prices = prices
        if len(prices) >= 2:
            self._is_positive = prices[-1] >= prices[0]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        pad_y = 4
        pad_x = 2

        prices = self._prices

        if len(prices) < 2:
            # Draw flat gray line
            painter.setPen(QPen(QColor("#444466"), 1.5))
            mid = h // 2
            painter.drawLine(pad_x, mid, w - pad_x, mid)
            painter.end()
            return

        min_p = min(prices)
        max_p = max(prices)
        range_p = (max_p - min_p) or 1.0
        usable_h = h - 2 * pad_y
        usable_w = w - 2 * pad_x
        n = len(prices)

        line_color = QColor(COLOR_SPARKLINE_UP if self._is_positive else COLOR_SPARKLINE_DOWN)
        fill_color = QColor(line_color)
        fill_color.setAlpha(45)

        def map_x(i: int) -> float:
            return pad_x + (i / (n - 1)) * usable_w

        def map_y(price: float) -> float:
            return pad_y + (1.0 - (price - min_p) / range_p) * usable_h

        points = [QPointF(map_x(i), map_y(p)) for i, p in enumerate(prices)]

        # Draw fill
        fill_path = QPainterPath()
        fill_path.moveTo(points[0].x(), h)
        for pt in points:
            fill_path.lineTo(pt)
        fill_path.lineTo(points[-1].x(), h)
        fill_path.closeSubpath()
        painter.fillPath(fill_path, fill_color)

        # Draw line
        line_path = QPainterPath()
        line_path.moveTo(points[0])
        for pt in points[1:]:
            line_path.lineTo(pt)
        pen = QPen(line_color, 1.5, Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(line_path)

        # Draw endpoint dot
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(line_color)
        last = points[-1]
        painter.drawEllipse(last, 2.5, 2.5)

        painter.end()
