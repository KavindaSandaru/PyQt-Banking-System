from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database import get_account_profile, update_account_profile, update_profile_picture
from ui.widgets.common import Avatar, COLORS, icon_label, with_shadow


class SettingsPage(QWidget):
    profile_changed = pyqtSignal()
    balance_privacy_changed = pyqtSignal(bool)

    def __init__(self, account_number):
        super().__init__()

        self.account_number = account_number
        self.setObjectName("SettingsPage")

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(42, 38, 42, 42)
        page_layout.setSpacing(24)

        page_layout.addWidget(self.build_header())
        page_layout.addWidget(self.build_account_card())
        page_layout.addWidget(self.build_ui_card())
        page_layout.addStretch()

        self.refresh()

    def build_header(self):
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title = QLabel("Settings")
        title.setObjectName("PageTitle")

        subtitle = QLabel("Account settings, profile photo, and interface preferences")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        return header

    def build_account_card(self):
        card = QFrame()
        card.setObjectName("FormCard")
        with_shadow(card, blur=30, y=10, alpha=85)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 28, 30, 30)
        layout.setSpacing(22)

        title = QLabel("Account Settings")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        profile_row = QHBoxLayout()
        profile_row.setSpacing(18)

        self.avatar = Avatar()
        self.avatar.clicked.connect(self.choose_profile_picture)
        profile_row.addWidget(self.avatar)

        profile_text = QVBoxLayout()
        profile_text.setSpacing(8)
        profile_text.addWidget(QLabel("Profile picture"))

        photo_button = QPushButton("Choose Photo")
        photo_button.setObjectName("SecondaryButton")
        photo_button.clicked.connect(self.choose_profile_picture)
        profile_text.addWidget(photo_button)

        profile_row.addLayout(profile_text, 1)
        layout.addLayout(profile_row)

        form = QGridLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(14)

        self.account_input = QLineEdit()
        self.account_input.setReadOnly(True)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")

        self.birthday_input = QLineEdit()
        self.birthday_input.setPlaceholderText("Birthday, e.g. 2000-01-01")

        form.addWidget(self.field_label("Account Number"), 0, 0)
        form.addWidget(self.account_input, 0, 1)
        form.addWidget(self.field_label("Full Name"), 1, 0)
        form.addWidget(self.name_input, 1, 1)
        form.addWidget(self.field_label("Birthday"), 2, 0)
        form.addWidget(self.birthday_input, 2, 1)

        layout.addLayout(form)

        save_button = QPushButton("Save Account Settings")
        save_button.setObjectName("PrimaryButton")
        save_button.clicked.connect(self.save_account_settings)
        layout.addWidget(save_button)

        return card

    def build_ui_card(self):
        card = QFrame()
        card.setObjectName("FormCard")
        with_shadow(card, blur=24, y=8, alpha=70)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 24, 30, 26)
        layout.setSpacing(18)

        row = QHBoxLayout()
        row.setSpacing(16)
        row.addWidget(icon_label("settings", COLORS["blue_soft"], "#173d9a", 58))

        text = QVBoxLayout()
        title = QLabel("UI Preferences")
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Small display options for the banking dashboard")
        subtitle.setObjectName("MutedLabel")
        text.addWidget(title)
        text.addWidget(subtitle)
        row.addLayout(text, 1)
        layout.addLayout(row)

        self.blur_checkbox = QCheckBox("Blur balance by default")
        self.blur_checkbox.toggled.connect(self.balance_privacy_changed.emit)
        self.compact_checkbox = QCheckBox("Use compact transaction rows")
        self.accent_select = QComboBox()
        self.accent_select.addItems(["Blue accent", "Green accent", "Purple accent"])

        layout.addWidget(self.blur_checkbox)
        layout.addWidget(self.compact_checkbox)
        layout.addWidget(self.accent_select)

        return card

    def field_label(self, text):
        label = QLabel(text)
        label.setObjectName("MutedLabel")
        return label

    def refresh(self):
        profile = get_account_profile(self.account_number)
        self.account_input.setText(profile["account_number"])
        self.name_input.setText(profile["name"])
        self.birthday_input.setText(profile["birthday"])
        self.avatar.set_profile_picture(profile["profile_picture"])

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

    def save_account_settings(self):
        name = self.name_input.text().strip()
        birthday = self.birthday_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Settings", "Enter your full name.")
            return

        if birthday and not QDate.fromString(birthday, "yyyy-MM-dd").isValid():
            QMessageBox.warning(self, "Settings", "Use birthday format YYYY-MM-DD.")
            return

        if update_account_profile(self.account_number, name, birthday):
            self.profile_changed.emit()
            QMessageBox.information(self, "Settings", "Account settings saved.")
