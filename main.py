from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import DARK_STYLE


def create_app() -> QApplication:
    app = QApplication(sys.argv)
    app.setApplicationName("OConf")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("OConf")
    app.setStyleSheet(DARK_STYLE)
    return app


def main():
    app = create_app()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
