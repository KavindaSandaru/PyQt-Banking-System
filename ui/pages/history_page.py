from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from database import get_transactions
from ui.widgets.common import (
    COLORS,
    StatPill,
    amount_color,
    icon_label,
    is_inflow,
    readable_datetime,
    signed_money,
    with_shadow,
)


class HistoryPage(QWidget):
    def __init__(self, account_number):
        super().__init__()

        self.account_number = account_number
        self.list_layout = QVBoxLayout()

        self.setObjectName("HistoryPage")

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(42, 38, 42, 42)
        page_layout.setSpacing(24)

        page_layout.addWidget(self.build_header())
        page_layout.addWidget(self.build_history_panel(), 1)

        self.refresh()

    def build_header(self):
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title = QLabel("History")
        title.setObjectName("PageTitle")

        subtitle = QLabel("Your completed transactions")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        return header

    def build_history_panel(self):
        panel = QFrame()
        panel.setObjectName("RecentPanel")
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        with_shadow(panel, blur=30, y=8, alpha=70)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        title = QLabel("All Transactions")
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

        transactions = get_transactions(self.account_number)

        if not transactions:
            empty = QLabel("No transactions yet")
            empty.setObjectName("MutedLabel")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(empty, 1)
            return

        for index, transaction in enumerate(transactions):
            self.list_layout.addWidget(self.transaction_row(transaction))

            if index < len(transactions) - 1:
                separator = QFrame()
                separator.setObjectName("RowSeparator")
                separator.setFixedHeight(1)
                self.list_layout.addWidget(separator)

        self.list_layout.addStretch()

    def transaction_row(self, transaction):
        _, _, transaction_type, amount, created_at, description = transaction
        row = QWidget()
        row.setObjectName("TransactionRow")
        row.setMinimumHeight(72)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)

        kind = "deposit" if is_inflow(transaction_type) else "withdraw"
        bg = "#123d35" if is_inflow(transaction_type) else "#493014"

        if "Transfer" in transaction_type:
            kind = "transfer"
            bg = "#2e205f"

        color = amount_color(transaction_type)
        layout.addWidget(icon_label(kind, color, bg, 52))

        text = QVBoxLayout()
        text.setSpacing(3)
        title = QLabel(description or transaction_type)
        title.setObjectName("TransactionTitle")

        meta = QLabel(readable_datetime(created_at))
        meta.setObjectName("MutedLabel")

        text.addWidget(title)
        text.addWidget(meta)
        layout.addLayout(text, 1)

        amount_label = QLabel(signed_money(transaction_type, amount))
        amount_label.setObjectName("TransactionAmount")
        amount_label.setStyleSheet(f"color: {color};")
        amount_label.setMinimumWidth(160)
        amount_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(amount_label)

        layout.addWidget(StatPill("Completed"))

        return row

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()

            if widget:
                widget.deleteLater()
            elif child_layout:
                self.clear_layout(child_layout)
