import sqlite3

from PyQt6.QtCore import Qt
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

from database import create_account, get_account
from ui.main_window import MainWindow
from ui.widgets.common import COLORS, display_name, icon_label, with_shadow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.main_window = None
        self.setWindowTitle("ATM Login")
        self.setMinimumSize(520, 560)
        self.resize(540, 600)
        self.setObjectName("LoginWindow")

        root = QVBoxLayout(self)
        root.setContentsMargins(42, 42, 42, 42)
        root.setSpacing(0)
        root.addStretch()

        card = QFrame()
        card.setObjectName("LoginCard")
        with_shadow(card, blur=34, y=12, alpha=110)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(34, 34, 34, 34)
        layout.setSpacing(18)

        brand = QHBoxLayout()
        brand.setSpacing(16)
        brand.addWidget(icon_label("bank", "#98b6ff", "#173d9a", 64))

        brand_text = QVBoxLayout()
        brand_text.setSpacing(2)
        title = QLabel("ATM")
        title.setObjectName("BrandTitle")
        subtitle = QLabel("Banking System")
        subtitle.setObjectName("BrandSubtitle")
        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)
        brand.addLayout(brand_text, 1)

        layout.addLayout(brand)

        heading = QLabel("Welcome back")
        heading.setObjectName("LoginTitle")
        layout.addWidget(heading)

        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("Account Number")
        layout.addWidget(self.account_input)

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("PIN")
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.returnPressed.connect(self.login)
        layout.addWidget(self.pin_input)

        login_button = QPushButton("Login")
        login_button.setObjectName("PrimaryButton")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        create_button = QPushButton("Create Account")
        create_button.setObjectName("SecondaryButton")
        create_button.clicked.connect(self.create_new_account)
        layout.addWidget(create_button)

        root.addWidget(card)
        root.addStretch()

    def login(self):
        account_number = self.account_input.text().strip()
        pin = self.pin_input.text().strip()

        if not account_number or not pin:
            QMessageBox.warning(self, "Login Failed", "Enter your account number and PIN.")
            return

        account = get_account(account_number)

        if account is None:
            QMessageBox.warning(self, "Login Failed", "Account not found.")
            return

        stored_pin = account[1]

        if pin != stored_pin:
            QMessageBox.warning(self, "Login Failed", "Invalid PIN.")
            return

        self.main_window = MainWindow(account_number, self.show_login_again)
        self.main_window.show()
        self.hide()

    def create_new_account(self):
        account_number = self.account_input.text().strip()
        pin = self.pin_input.text().strip()

        if not account_number or not pin:
            QMessageBox.warning(self, "Create Account", "Enter an account number and PIN.")
            return

        if len(pin) < 4:
            QMessageBox.warning(self, "Create Account", "PIN must be at least 4 digits.")
            return

        try:
            create_account(account_number, pin)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Create Account", "That account already exists.")
            return

        QMessageBox.information(
            self,
            "Account Created",
            f"{display_name(account_number)} is ready to use.",
        )

    def show_login_again(self):
        self.pin_input.clear()
        self.show()
        self.activateWindow()
