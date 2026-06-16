from __future__ import annotations

import os
import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import DARK_STYLE

__version__ = os.environ.get("OCONF_VERSION", "1.0.0")


def create_app() -> QApplication:
    app = QApplication(sys.argv)
    app.setApplicationName("OConf")
    app.setApplicationVersion(__version__)
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
