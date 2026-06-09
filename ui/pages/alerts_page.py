from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from database import get_alerts, mark_alerts_read
from ui.widgets.common import COLORS, icon_label, readable_datetime, with_shadow


class AlertsPage(QWidget):
    def __init__(self, account_number, on_read=None):
        super().__init__()

        self.account_number = account_number
        self.on_read = on_read
        self.list_layout = QVBoxLayout()

        self.setObjectName("AlertsPage")

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(42, 38, 42, 42)
        page_layout.setSpacing(24)

        page_layout.addWidget(self.build_header())
        page_layout.addWidget(self.build_alert_panel(), 1)

        self.refresh()

    def build_header(self):
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        text = QVBoxLayout()
        text.setSpacing(6)

        title = QLabel("Alerts")
        title.setObjectName("PageTitle")

        subtitle = QLabel("Security notices, failed login attempts, and recent account changes")
        subtitle.setObjectName("PageSubtitle")

        text.addWidget(title)
        text.addWidget(subtitle)
        layout.addLayout(text, 1)

        mark_read = QPushButton("Mark All Read")
        mark_read.setObjectName("SecondaryButton")
        mark_read.clicked.connect(self.mark_all_read)
        layout.addWidget(mark_read)

        return header

    def build_alert_panel(self):
        panel = QFrame()
        panel.setObjectName("RecentPanel")
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        with_shadow(panel, blur=30, y=8, alpha=70)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        title = QLabel("Recent Alerts")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        separator = QFrame()
        separator.setObjectName("PanelSeparator")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        scroll = QScrollArea()
        scroll.setObjectName("HistoryScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        self.list_layout = QVBoxLayout(content)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        scroll.setWidget(content)

        layout.addWidget(scroll, 1)

        return panel

    def refresh(self):
        self.clear_layout(self.list_layout)
        alerts = get_alerts(self.account_number)

        if not alerts:
            empty = QLabel("No alerts yet")
            empty.setObjectName("MutedLabel")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(empty, 1)
            return

        for index, alert in enumerate(alerts):
            self.list_layout.addWidget(self.alert_row(alert))

            if index < len(alerts) - 1:
                separator = QFrame()
                separator.setObjectName("RowSeparator")
                separator.setFixedHeight(1)
                self.list_layout.addWidget(separator)

        self.list_layout.addStretch()

    def alert_row(self, alert):
        _, title, message, category, created_at, read = alert
        row = QWidget()
        row.setObjectName("AlertRow")
        row.setMinimumHeight(82)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(16)

        color = COLORS["orange"] if category == "Security" else COLORS["blue_soft"]
        bg = "#493014" if category == "Security" else "#173d9a"
        layout.addWidget(icon_label("bell", color, bg, 52))

        text = QVBoxLayout()
        text.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("TransactionTitle")

        message_label = QLabel(message)
        message_label.setObjectName("MutedLabel")
        message_label.setWordWrap(True)

        date_label = QLabel(readable_datetime(created_at))
        date_label.setObjectName("MutedLabel")

        text.addWidget(title_label)
        text.addWidget(message_label)
        text.addWidget(date_label)
        layout.addLayout(text, 1)

        badge = QLabel("New" if not read else "Read")
        badge.setObjectName("StatusPill" if not read else "ReadPill")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setMinimumWidth(82)
        layout.addWidget(badge)

        return row

    def mark_all_read(self):
        mark_alerts_read(self.account_number)
        self.refresh()
        if self.on_read:
            self.on_read()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()

            if widget:
                widget.deleteLater()
            elif child_layout:
                self.clear_layout(child_layout)
