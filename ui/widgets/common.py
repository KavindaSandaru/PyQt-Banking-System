from datetime import datetime

from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPoint, QPointF, QPropertyAnimation, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


COLORS = {
    "blue": "#2f6bff",
    "blue_soft": "#5a8cff",
    "green": "#44e879",
    "orange": "#ff9417",
    "purple": "#9a66ff",
    "red": "#ff4f5f",
    "text": "#f7fbff",
    "muted": "#9aa9c5",
    "panel": "#101b2e",
    "panel_alt": "#0c1728",
    "stroke": "#21314f",
}


def money(value):
    return f"${float(value):,.2f}"


def display_name(account_number):
    names = {
        "1999": "Ishan",
        "1998": "John Doe",
        "admin": "Admin",
    }
    return names.get(str(account_number), f"Account {account_number}")


def parse_datetime(value):
    if not value:
        return None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value[:19], fmt)
        except ValueError:
            pass

    return None


def readable_datetime(value):
    parsed = parse_datetime(value)

    if not parsed:
        return "Recent"

    return parsed.strftime("%b %d, %Y - %I:%M %p").replace(" 0", " ")


def amount_color(transaction_type):
    if transaction_type in ("Deposit", "Transfer In"):
        return COLORS["green"]

    return COLORS["red"]


def signed_money(transaction_type, value):
    sign = "+" if transaction_type in ("Deposit", "Transfer In") else "-"
    return f"{sign}{money(value)}"


def is_inflow(transaction_type):
    return transaction_type in ("Deposit", "Transfer In")


def with_shadow(widget, blur=24, y=10, alpha=90):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, y)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)
    return widget


def make_panel(object_name="Card"):
    panel = QFrame()
    panel.setObjectName(object_name)
    panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return with_shadow(panel, blur=28, y=8, alpha=70)


def _draw_arrow_down(painter, rect, color):
    pen = QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(rect.center().x(), rect.top() + 5, rect.center().x(), rect.bottom() - 13)
    painter.drawLine(rect.center().x(), rect.bottom() - 13, rect.left() + 9, rect.bottom() - 24)
    painter.drawLine(rect.center().x(), rect.bottom() - 13, rect.right() - 9, rect.bottom() - 24)
    painter.drawLine(rect.left() + 7, rect.bottom() - 7, rect.right() - 7, rect.bottom() - 7)
    painter.drawLine(rect.left() + 7, rect.bottom() - 7, rect.left() + 7, rect.bottom() - 19)
    painter.drawLine(rect.right() - 7, rect.bottom() - 7, rect.right() - 7, rect.bottom() - 19)


def _draw_arrow_up(painter, rect, color):
    pen = QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(rect.center().x(), rect.bottom() - 5, rect.center().x(), rect.top() + 13)
    painter.drawLine(rect.center().x(), rect.top() + 13, rect.left() + 9, rect.top() + 24)
    painter.drawLine(rect.center().x(), rect.top() + 13, rect.right() - 9, rect.top() + 24)
    painter.drawLine(rect.left() + 7, rect.bottom() - 7, rect.right() - 7, rect.bottom() - 7)
    painter.drawLine(rect.left() + 7, rect.bottom() - 7, rect.left() + 7, rect.bottom() - 19)
    painter.drawLine(rect.right() - 7, rect.bottom() - 7, rect.right() - 7, rect.bottom() - 19)


def _draw_transfer(painter, rect, color):
    pen = QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    y1 = rect.top() + rect.height() * 0.35
    y2 = rect.top() + rect.height() * 0.65
    painter.drawLine(rect.left() + 7, int(y1), rect.right() - 9, int(y1))
    painter.drawLine(rect.right() - 9, int(y1), rect.right() - 19, int(y1) - 9)
    painter.drawLine(rect.right() - 9, int(y1), rect.right() - 19, int(y1) + 9)
    painter.drawLine(rect.right() - 7, int(y2), rect.left() + 9, int(y2))
    painter.drawLine(rect.left() + 9, int(y2), rect.left() + 19, int(y2) - 9)
    painter.drawLine(rect.left() + 9, int(y2), rect.left() + 19, int(y2) + 9)


def _draw_dashboard(painter, rect, color):
    painter.setPen(QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    size = max(8, rect.width() // 4)
    gap = max(6, rect.width() // 8)
    x = rect.left() + 8
    y = rect.top() + 8
    for row in range(2):
        for col in range(2):
            painter.drawRoundedRect(x + col * (size + gap), y + row * (size + gap), size, size, 3, 3)


def _draw_history(painter, rect, color):
    pen = QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(rect.left() + 9, rect.top() + 7, rect.width() - 18, rect.height() - 13, 4, 4)
    painter.drawLine(rect.right() - 17, rect.top() + 7, rect.right() - 17, rect.top() + 18)
    painter.drawLine(rect.right() - 17, rect.top() + 18, rect.right() - 7, rect.top() + 18)
    painter.drawEllipse(rect.center().x() - 2, rect.center().y() + 1, 12, 12)
    painter.drawLine(rect.center().x() + 4, rect.center().y() + 7, rect.center().x() + 4, rect.center().y() + 3)
    painter.drawLine(rect.center().x() + 4, rect.center().y() + 7, rect.center().x() + 9, rect.center().y() + 7)


def _draw_bank(painter, rect, color):
    pen = QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(QColor(color))
    roof = QPolygonF(
        [
            QPointF(rect.center().x(), rect.top() + 4),
            QPointF(rect.right() - 4, rect.top() + 16),
            QPointF(rect.left() + 4, rect.top() + 16),
        ]
    )
    painter.drawPolygon(roof)
    painter.drawRect(rect.left() + 8, rect.top() + 20, rect.width() - 16, 5)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    for i in range(3):
        x = rect.left() + 11 + i * ((rect.width() - 22) // 3)
        painter.drawLine(x, rect.top() + 28, x, rect.bottom() - 9)
    painter.drawLine(rect.left() + 6, rect.bottom() - 5, rect.right() - 6, rect.bottom() - 5)


def _draw_logout(painter, rect, color):
    pen = QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(rect.left() + 5, rect.top() + 8, rect.width() - 20, rect.height() - 16, 4, 4)
    painter.drawLine(rect.center().x(), rect.center().y(), rect.right() - 5, rect.center().y())
    painter.drawLine(rect.right() - 5, rect.center().y(), rect.right() - 14, rect.center().y() - 8)
    painter.drawLine(rect.right() - 5, rect.center().y(), rect.right() - 14, rect.center().y() + 8)


def _draw_bell(painter, rect, color):
    pen = QPen(color, 3, Qt.PenStyle.SolidLine,
               Qt.PenCapStyle.RoundCap,
               Qt.PenJoinStyle.RoundJoin)

    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    center_x = rect.center().x()

    painter.drawArc(
        rect.left() + 6,
        rect.top() + 6,
        rect.width() - 12,
        rect.height() - 18,
        0,
        180 * 16
    )

    painter.drawLine(
        rect.left() + 10,
        rect.center().y(),
        rect.left() + 10,
        rect.bottom() - 10
    )

    painter.drawLine(
        rect.right() - 10,
        rect.center().y(),
        rect.right() - 10,
        rect.bottom() - 10
    )

    painter.drawLine(
        rect.left() + 10,
        rect.bottom() - 10,
        rect.right() - 10,
        rect.bottom() - 10
    )

    painter.drawEllipse(center_x - 3, rect.bottom() - 8, 6, 6)


def _draw_settings(painter, rect, color):
    pen = QPen(color, 3, Qt.PenStyle.SolidLine,
               Qt.PenCapStyle.RoundCap,
               Qt.PenJoinStyle.RoundJoin)

    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    center = rect.center()

    painter.drawEllipse(center.x() - 8, center.y() - 8, 16, 16)

    for angle in range(0, 360, 45):
        import math

        x1 = center.x() + int(math.cos(math.radians(angle)) * 12)
        y1 = center.y() + int(math.sin(math.radians(angle)) * 12)

        x2 = center.x() + int(math.cos(math.radians(angle)) * 20)
        y2 = center.y() + int(math.sin(math.radians(angle)) * 20)

        painter.drawLine(x1, y1, x2, y2)


def _draw_eye(painter, rect, color):
    pen = QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(rect.left() + 7, rect.center().y() - 9, rect.width() - 14, 18)
    painter.setBrush(QColor(color))
    painter.drawEllipse(rect.center().x() - 4, rect.center().y() - 4, 8, 8)


def make_icon(kind, color="#ffffff", bg_color=None, size=32):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    if bg_color:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(bg_color))
        painter.drawRoundedRect(0, 0, size, size, 8, 8)

    inset = max(5, size // 6)
    rect = pixmap.rect().adjusted(inset, inset, -inset, -inset)
    qcolor = QColor(color)

    if kind == "dashboard":
        _draw_dashboard(painter, rect, qcolor)
    elif kind == "deposit":
        _draw_arrow_down(painter, rect, qcolor)
    elif kind == "withdraw":
        _draw_arrow_up(painter, rect, qcolor)
    elif kind == "transfer":
        _draw_transfer(painter, rect, qcolor)
    elif kind == "history":
        _draw_history(painter, rect, qcolor)
    elif kind == "bank":
        _draw_bank(painter, rect, qcolor)
    elif kind == "logout":
        _draw_logout(painter, rect, qcolor)
    elif kind == "bell":
        _draw_bell(painter, rect, qcolor)
    elif kind == "settings":
        _draw_settings(painter, rect, qcolor)
    elif kind == "eye":
        _draw_eye(painter, rect, qcolor)
    else:
        painter.setPen(QPen(qcolor, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawEllipse(rect)

    painter.end()
    return QIcon(pixmap)


def icon_pixmap(kind, color="#ffffff", bg_color=None, size=54):
    return make_icon(kind, color, bg_color, size).pixmap(QSize(size, size))


def icon_label(kind, color, bg_color=None, size=54):
    label = QLabel()
    label.setObjectName("IconBadge")
    label.setFixedSize(size, size)
    label.setPixmap(icon_pixmap(kind, color, bg_color, size))
    label.setScaledContents(False)
    return label


class IconButton(QPushButton):
    def __init__(self, kind, color="#ffffff", tooltip="", parent=None):
        super().__init__(parent)

        self.setObjectName("IconButton")
        self.setFixedSize(46, 46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        icons = {
            "bell": "🔔",
            "settings": "⚙",
        }

        self.setText(icons.get(kind, "•"))

        font = self.font()
        font.setPointSize(16)
        self.setFont(font)

        if tooltip:
            self.setToolTip(tooltip)


class Avatar(QWidget):
    clicked = pyqtSignal()

    def __init__(self, profile_picture="", parent=None):
        super().__init__(parent)
        self.profile_picture = profile_picture
        self.setFixedSize(64, 64)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Change profile picture")

    def set_profile_picture(self, profile_picture):
        self.profile_picture = profile_picture or ""
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        photo = None
        if self.profile_picture and Path(self.profile_picture).exists():
            photo = QPixmap(self.profile_picture)

        if photo and not photo.isNull():
            path = QPainterPath()
            path.addEllipse(0, 0, 58, 58)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, 58, 58, photo.scaled(58, 58, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            painter.setClipping(False)
            painter.setPen(QPen(QColor("#d8e3ff"), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(1, 1, 56, 56)
            painter.setBrush(QColor(COLORS["green"]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(48, 45, 14, 14)
            painter.end()
            return

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#c9d8ff"))
        painter.drawEllipse(0, 0, 58, 58)

        painter.setBrush(QColor("#f1a163"))
        painter.drawEllipse(21, 12, 17, 18)

        painter.setBrush(QColor("#151b2c"))
        painter.drawPie(19, 8, 21, 16, 0, 180 * 16)

        painter.setBrush(QColor("#f5f7ff"))
        painter.drawRoundedRect(18, 32, 24, 20, 8, 8)

        painter.setBrush(QColor("#e3344f"))
        painter.drawPolygon(
            QPolygonF(
                [
                    QPointF(29, 33),
                    QPointF(34, 33),
                    QPointF(33, 52),
                    QPointF(30, 52),
                ]
            )
        )

        painter.setBrush(QColor(COLORS["green"]))
        painter.drawEllipse(48, 45, 14, 14)
        painter.end()


class AtmIllustration(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(190)
        self.setMaximumHeight(230)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(22, 45, 119, 110))
        painter.drawEllipse(4, h - 26, w - 8, 24)

        for side in (-1, 1):
            stem_x = int(w * (0.26 if side < 0 else 0.76))
            painter.setPen(QPen(QColor(43, 82, 190, 130), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(stem_x, h - 35, stem_x + side * 26, h - 90)
            painter.setBrush(QColor(41, 78, 180, 145))
            painter.setPen(Qt.PenStyle.NoPen)
            for i in range(4):
                leaf_y = h - 52 - i * 20
                painter.drawEllipse(stem_x + side * (8 + i * 4), leaf_y, 24, 12)

        body = QLinearGradient(0, 30, 0, h - 28)
        body.setColorAt(0, QColor("#2c55d6"))
        body.setColorAt(1, QColor("#162758"))
        painter.setBrush(body)
        painter.drawRoundedRect(int(w * 0.34), 35, int(w * 0.38), h - 56, 14, 14)

        painter.setBrush(QColor("#203f9f"))
        painter.drawRoundedRect(int(w * 0.31), 22, int(w * 0.44), 38, 18, 18)

        painter.setBrush(QColor("#0a1430"))
        painter.drawRoundedRect(int(w * 0.39), 70, int(w * 0.28), 54, 9, 9)
        painter.setBrush(QColor("#334fc9"))
        painter.drawRoundedRect(int(w * 0.41), 76, int(w * 0.24), 40, 6, 6)

        painter.setBrush(QColor("#0d1835"))
        painter.drawRoundedRect(int(w * 0.42), 138, int(w * 0.19), 10, 3, 3)
        painter.drawRoundedRect(int(w * 0.63), 142, int(w * 0.06), 6, 3, 3)
        painter.setBrush(QColor("#315fe4"))
        painter.drawRoundedRect(int(w * 0.47), 154, int(w * 0.13), 8, 3, 3)

        painter.setPen(QPen(QColor("#476fff"), 2))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(int(w * 0.47), 42, "ATM")
        painter.end()


class BankWatermark(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(260)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(0.14)

        color = QColor("#78a5ff")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        w = self.width()
        h = self.height()

        roof = QPolygonF(
            [
                QPointF(int(w * 0.5), int(h * 0.16)),
                QPointF(int(w * 0.9), int(h * 0.52)),
                QPointF(int(w * 0.1), int(h * 0.52)),
            ]
        )
        painter.drawPolygon(roof)
        painter.drawRoundedRect(int(w * 0.15), int(h * 0.58), int(w * 0.7), 16, 5, 5)

        for x in (0.25, 0.5, 0.75):
            painter.drawRoundedRect(int(w * x) - 18, int(h * 0.72), 36, int(h * 0.5), 4, 4)

        painter.end()


class ActionButton(QPushButton):
    def __init__(self, kind, title, subtitle, amount, color, parent=None):
        super().__init__(parent)
        self.setObjectName("ActionButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(112)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(18)

        layout.addWidget(icon_label(kind, color, QColor(color).darker(260).name(), 60))

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("ActionTitle")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("MutedLabel")

        amount_label = QLabel(amount)
        amount_label.setObjectName("ActionAmount")
        amount_label.setStyleSheet(f"color: {color};")

        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)
        text_layout.addWidget(amount_label)
        layout.addLayout(text_layout, 1)


class StatPill(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("StatusPill")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(112)


class TitleBar(QFrame):
    def __init__(self, title, icon, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self._drag_start = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 16, 0)
        layout.setSpacing(10)

        icon_label_widget = QLabel()
        icon_label_widget.setPixmap(icon_pixmap(icon, "#98b6ff", "#1e46a8", 28))
        icon_label_widget.setFixedSize(32, 32)

        title_label = QLabel(title)
        title_label.setObjectName("WindowTitle")

        layout.addWidget(icon_label_widget)
        layout.addWidget(title_label)
        layout.addStretch()

        self.minimize_button = QPushButton("-")
        self.maximize_button = QPushButton("[]")
        self.close_button = QPushButton("X")

        for button in (self.minimize_button, self.maximize_button, self.close_button):
            button.setObjectName("WindowButton")
            button.setFixedSize(36, 32)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(button)

        self.close_button.setObjectName("CloseButton")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_start is None:
            return

        window = self.window()
        delta = event.globalPosition().toPoint() - self._drag_start
        window.move(window.pos() + delta)
        self._drag_start = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_start = None


class FadeInMixin:
    def fade_in(self):
        self.setWindowOpacity(0)
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(220)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        self._fade_animation = animation
