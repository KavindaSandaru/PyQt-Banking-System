from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.pages.alerts_page import AlertsPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.deposit_page import DepositPage
from ui.pages.history_page import HistoryPage
from ui.pages.settings_page import SettingsPage
from ui.pages.transfer_page import TransferPage
from ui.pages.withdraw_page import WithdrawPage
from ui.widgets.common import (
    AtmIllustration,
    Avatar,
    COLORS,
    TitleBar,
    display_name,
    icon_label,
    make_icon,
)


class MainWindow(QWidget):
    def __init__(self, account_number, on_logout=None):
        super().__init__()

        self.account_number = account_number
        self.on_logout = on_logout
        self.nav_buttons = {}

        self.setWindowTitle("ATM Management System")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setMinimumSize(1120, 720)
        self.resize(1280, 790)
        self.setObjectName("AppWindow")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.title_bar = TitleBar("ATM Management System", "bank", self)
        self.title_bar.minimize_button.clicked.connect(self.showMinimized)
        self.title_bar.maximize_button.clicked.connect(self.toggle_maximized)
        self.title_bar.close_button.clicked.connect(self.close)
        root_layout.addWidget(self.title_bar)

        shell = QFrame()
        shell.setObjectName("MainShell")
        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        shell_layout.addWidget(self.build_sidebar())

        self.pages = QStackedWidget()
        self.pages.setObjectName("PageStack")
        self.pages.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.dashboard_page = DashboardPage(self.account_number)
        self.deposit_page = DepositPage(self.account_number, self.refresh_pages)
        self.withdraw_page = WithdrawPage(self.account_number, self.refresh_pages)
        self.transfer_page = TransferPage(self.account_number, self.refresh_pages)
        self.history_page = HistoryPage(self.account_number)
        self.alerts_page = AlertsPage(self.account_number, self.refresh_alert_state)
        self.settings_page = SettingsPage(self.account_number)

        self.dashboard_page.navigate_requested.connect(self.show_page)
        self.dashboard_page.profile_changed.connect(self.refresh_pages)
        self.settings_page.profile_changed.connect(self.refresh_pages)
        self.settings_page.profile_changed.connect(lambda: self.show_page("Dashboard"))

        self.page_map = {
            "Dashboard": self.dashboard_page,
            "Deposit": self.deposit_page,
            "Withdraw": self.withdraw_page,
            "Transfer": self.transfer_page,
            "History": self.history_page,
            "Alerts": self.alerts_page,
            "Settings": self.settings_page,
        }

        for page in self.page_map.values():
            self.pages.addWidget(page)

        shell_layout.addWidget(self.pages, 1)
        root_layout.addWidget(shell, 1)

        self.show_page("Dashboard")

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(270)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(24, 30, 24, 26)
        layout.setSpacing(14)

        brand = QWidget()
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(0, 0, 0, 20)
        brand_layout.setSpacing(14)

        brand_layout.addWidget(icon_label("bank", "#98b6ff", "#173d9a", 58))

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)

        title = QLabel("ATM")
        title.setObjectName("BrandTitle")
        subtitle = QLabel("Banking System")
        subtitle.setObjectName("BrandSubtitle")

        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)
        brand_layout.addLayout(brand_text)

        layout.addWidget(brand)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_items = [
            ("Dashboard", "dashboard", COLORS["blue_soft"]),
            ("Deposit", "deposit", COLORS["green"]),
            ("Withdraw", "withdraw", COLORS["orange"]),
            ("Transfer", "transfer", COLORS["purple"]),
            ("History", "history", "#ffd44a"),
        ]

        for label, icon, color in nav_items:
            button = self.create_nav_button(label, icon, color)
            self.nav_buttons[label] = button
            self.nav_group.addButton(button)
            layout.addWidget(button)

        separator = QFrame()
        separator.setObjectName("SidebarSeparator")
        separator.setFixedHeight(1)
        layout.addSpacing(14)
        layout.addWidget(separator)

        logout_button = self.create_nav_button("Logout", "logout", COLORS["red"])
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

        layout.addStretch()
        layout.addWidget(AtmIllustration())

        return sidebar

    def create_nav_button(self, label, icon, color):
        button = QPushButton(label)
        button.setProperty("nav", True)
        button.setProperty("active", False)
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIcon(make_icon(icon, color, None, 32))
        button.setIconSize(QSize(28, 28))
        button.clicked.connect(lambda checked=False, page=label: self.show_page(page))
        return button

    def show_page(self, page_name):
        page = self.page_map.get(page_name)

        if page is None:
            return

        self.pages.setCurrentWidget(page)

        if hasattr(page, "refresh"):
            page.refresh()

        for name, button in self.nav_buttons.items():
            is_active = name == page_name
            button.setChecked(is_active)
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def refresh_pages(self):
        self.dashboard_page.refresh()
        self.history_page.refresh()
        self.alerts_page.refresh()
        self.settings_page.refresh()

        current = self.pages.currentWidget()
        if hasattr(current, "refresh"):
            current.refresh()

    def refresh_alert_state(self):
        self.dashboard_page.refresh()

    def toggle_maximized(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def logout(self):
        if self.on_logout:
            self.on_logout()
        self.close()
