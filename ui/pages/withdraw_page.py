from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database import get_balance, withdraw
from ui.widgets.common import COLORS, icon_label, money, with_shadow


class WithdrawPage(QWidget):
    def __init__(self, account_number, on_complete=None):
        super().__init__()

        self.account_number = account_number
        self.on_complete = on_complete
        self.balance_label = QLabel()
        self.balance_label.setObjectName("FormBalance")

        self.setObjectName("FormPage")

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(42, 38, 42, 42)
        page_layout.setSpacing(24)

        page_layout.addWidget(self.build_header())
        page_layout.addWidget(self.build_form(), 0, Qt.AlignmentFlag.AlignTop)
        page_layout.addStretch()

        self.refresh()

    def build_header(self):
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title = QLabel("Withdraw")
        title.setObjectName("PageTitle")

        subtitle = QLabel("Withdraw cash from your account")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        return header

    def build_form(self):
        card = QFrame()
        card.setObjectName("FormCard")
        card.setMaximumWidth(620)
        with_shadow(card, blur=30, y=10, alpha=85)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 28, 30, 30)
        layout.setSpacing(20)

        summary = QHBoxLayout()
        summary.setSpacing(18)
        summary.addWidget(icon_label("withdraw", COLORS["orange"], "#493014", 66))

        text = QVBoxLayout()
        text.setSpacing(6)
        label = QLabel("Current Balance")
        label.setObjectName("MutedLabel")
        text.addWidget(label)
        text.addWidget(self.balance_label)
        summary.addLayout(text, 1)
        layout.addLayout(summary)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.amount_input.setValidator(QDoubleValidator(0.01, 1000000000, 2))
        layout.addWidget(self.amount_input)

        submit = QPushButton("Withdraw Cash")
        submit.setObjectName("PrimaryButton")
        submit.clicked.connect(self.make_withdrawal)
        layout.addWidget(submit)

        return card

    def make_withdrawal(self):
        amount = self.parse_amount()

        if amount is None:
            QMessageBox.warning(self, "Invalid Amount", "Enter a valid withdrawal amount.")
            return

        if withdraw(self.account_number, amount):
            self.amount_input.clear()
            self.refresh()
            if self.on_complete:
                self.on_complete()
            QMessageBox.information(self, "Withdrawal Complete", "Cash withdrawn successfully.")
        else:
            QMessageBox.warning(self, "Withdrawal Failed", "Insufficient funds or invalid amount.")

    def parse_amount(self):
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            return None

        return amount if amount > 0 else None

    def refresh(self):
        self.balance_label.setText(money(get_balance(self.account_number)))
