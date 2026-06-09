import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from database import seed_demo_data
from ui.login_window import LoginWindow


BASE_DIR = Path(__file__).resolve().parent


def load_stylesheet(app):
    style_path = BASE_DIR / "assets" / "styles" / "dark_theme.qss"

    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))


def main():
    seed_demo_data()

    app = QApplication(sys.argv)
    app.setApplicationName("ATM Management System")
    load_stylesheet(app)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
