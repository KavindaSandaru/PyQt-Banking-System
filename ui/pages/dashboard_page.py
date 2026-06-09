from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGraphicsBlurEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from database import (
    get_account_profile,
    get_balance,
    get_transactions,
    get_unread_alert_count,
    update_profile_picture,
)
from ui.widgets.common import (
    ActionButton,
    Avatar,
    BankWatermark,
    COLORS,
    IconButton,
    StatPill,
    amount_color,
    display_name,
    icon_label,
    is_inflow,
    make_icon,
    money,
    readable_datetime,
    signed_money,
    with_shadow,
)


class DashboardPage(QWidget):
    navigate_requested = pyqtSignal(str)
    profile_changed = pyqtSignal()

    def __init__(self, account_number):
        super().__init__()

        self.account_number = account_number
        self.balance_visible = False
        self.current_balance = 0
        self.title_label = QLabel()
        self.balance_label = QLabel()
        self.balance_label.setObjectName("BalanceAmount")
        self.recent_list = QVBoxLayout()

        self.setObjectName("DashboardPage")

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(34, 30, 34, 34)
        page_layout.setSpacing(22)

        page_layout.addWidget(self.build_header())
        page_layout.addWidget(self.build_balance_card())
        page_layout.addLayout(self.build_action_cards())
        page_layout.addWidget(self.build_recent_panel(), 1)

        self.refresh()

    def build_header(self):
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(6, 2, 4, 8)
        layout.setSpacing(16)

        text = QVBoxLayout()
        text.setSpacing(6)

        self.title_label.setObjectName("PageTitle")

        subtitle = QLabel("Here is your account overview")
        subtitle.setObjectName("PageSubtitle")

        text.addWidget(self.title_label)
        text.addWidget(subtitle)
        layout.addLayout(text, 1)

        self.alert_button = IconButton("bell", "#a7b9df", "Alerts")
        self.alert_button.clicked.connect(lambda: self.navigate_requested.emit("Alerts"))
        layout.addWidget(self.alert_button)

        settings_button = IconButton("settings", "#a7b9df", "Settings")
        settings_button.clicked.connect(lambda: self.navigate_requested.emit("Settings"))
        layout.addWidget(settings_button)

        self.avatar = Avatar()
        self.avatar.clicked.connect(self.choose_profile_picture)
        layout.addWidget(self.avatar)

        return header

    def build_balance_card(self):
        card = QFrame()
        card.setObjectName("BalanceCard")
        card.setMinimumHeight(176)
        with_shadow(card, blur=34, y=12, alpha=95)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(30, 26, 32, 26)
        layout.setSpacing(22)

        info = QVBoxLayout()
        info.setSpacing(8)

        label = QLabel("Current Balance")
        label.setObjectName("BalanceLabel")

        available = QLabel("Available Balance")
        available.setObjectName("BalanceLabel")

        info.addWidget(label)
        info.addWidget(self.balance_label)
        info.addStretch()
        info.addWidget(available)

        layout.addLayout(info, 1)

        self.eye_button = QPushButton()
        self.eye_button.setObjectName("BalanceEyeButton")
        self.eye_button.setIcon(make_icon("eye", "#ffffff", "#3c73ff", 56))
        self.eye_button.setIconSize(QSize(56, 56))
        self.eye_button.setFixedSize(64, 64)
        self.eye_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_button.setToolTip("Show balance")
        self.eye_button.clicked.connect(self.toggle_balance_visibility)
        layout.addWidget(self.eye_button)

        layout.addWidget(BankWatermark(), 0)

        return card

    def build_action_cards(self):
        actions = QHBoxLayout()
        actions.setSpacing(18)

        cards = [
            ("Deposit", "deposit", "Add money", "$50,000.00", COLORS["green"]),
            ("Withdraw", "withdraw", "Withdraw cash", "$5,000.00", COLORS["orange"]),
            ("Transfer", "transfer", "Send money", "$10,000.00", COLORS["purple"]),
            ("History", "history", "View history", "Open", COLORS["blue_soft"]),
        ]

        for page_name, kind, subtitle, amount, color in cards:
            action = ActionButton(kind, page_name, subtitle, amount, color)
            action.clicked.connect(lambda checked=False, page=page_name: self.navigate_requested.emit(page))
            actions.addWidget(action, 1)

        return actions

    def build_recent_panel(self):
        panel = QFrame()
        panel.setObjectName("RecentPanel")
        panel.setMinimumHeight(290)
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        with_shadow(panel, blur=30, y=8, alpha=70)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 22, 24, 18)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Recent Transactions")
        title.setObjectName("SectionTitle")
        view_all = QPushButton("View All")
        view_all.setObjectName("LinkButton")
        view_all.clicked.connect(lambda: self.navigate_requested.emit("History"))

        header.addWidget(title)
        header.addStretch()
        header.addWidget(view_all)

        layout.addLayout(header)

        separator = QFrame()
        separator.setObjectName("PanelSeparator")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        self.recent_list.setSpacing(0)
        layout.addLayout(self.recent_list)

        return panel

    def refresh(self):
        profile = get_account_profile(self.account_number)
        self.title_label.setText(f"Welcome back, {profile['name']}")
        self.avatar.set_profile_picture(profile["profile_picture"])
        self.alert_button.setToolTip(
            f"Alerts ({get_unread_alert_count(self.account_number)} unread)"
        )

        balance = get_balance(self.account_number)
        self.current_balance = balance
        self.update_balance_label()

        self.clear_layout(self.recent_list)

        transactions = get_transactions(self.account_number, limit=4)

        if not transactions:
            empty = QLabel("No recent transactions")
            empty.setObjectName("MutedLabel")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recent_list.addWidget(empty, 1)
            return

        for index, transaction in enumerate(transactions):
            row = self.transaction_row(transaction)
            self.recent_list.addWidget(row)

            if index < len(transactions) - 1:
                separator = QFrame()
                separator.setObjectName("RowSeparator")
                separator.setFixedHeight(1)
                self.recent_list.addWidget(separator)

        self.recent_list.addStretch()

    def toggle_balance_visibility(self):
        self.balance_visible = not self.balance_visible
        self.update_balance_label()

    def update_balance_label(self):
        self.balance_label.setText(money(self.current_balance))

        if self.balance_visible:
            self.balance_label.setGraphicsEffect(None)
            self.eye_button.setToolTip("Blur balance")
            return

        blur = QGraphicsBlurEffect(self.balance_label)
        blur.setBlurRadius(11)
        self.balance_label.setGraphicsEffect(blur)
        self.eye_button.setToolTip("Show balance")

    def choose_profile_picture(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Profile Picture",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )

        if not file_path:
            return

        if update_profile_picture(self.account_number, file_path):
            self.avatar.set_profile_picture(file_path)
            self.profile_changed.emit()

    def transaction_row(self, transaction):
        _, _, transaction_type, amount, created_at, description = transaction
        row = QWidget()
        row.setObjectName("TransactionRow")
        row.setMinimumHeight(68)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)

        kind = "deposit" if is_inflow(transaction_type) else "withdraw"
        if "Transfer" in transaction_type:
            kind = "transfer"

        color = amount_color(transaction_type)
        bg = "#123d35" if is_inflow(transaction_type) else "#493014"
        if "Transfer" in transaction_type:
            bg = "#2e205f"

        layout.addWidget(icon_label(kind, color, bg, 52))

        text = QVBoxLayout()
        text.setSpacing(3)

        label = description or transaction_type
        title = QLabel(label)
        title.setObjectName("TransactionTitle")

        date = QLabel(readable_datetime(created_at))
        date.setObjectName("MutedLabel")

        text.addWidget(title)
        text.addWidget(date)
        layout.addLayout(text, 1)

        amount_label = QLabel(signed_money(transaction_type, amount))
        amount_label.setObjectName("TransactionAmount")
        amount_label.setStyleSheet(f"color: {color};")
        amount_label.setMinimumWidth(150)
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
