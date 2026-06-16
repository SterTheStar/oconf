from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QStatusBar, QWidget


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)

        self.file_label = QLabel("No file loaded")
        self.status_label = QLabel("Ready")
        self.errors_label = QLabel("")

        self.addWidget(self.file_label, 1)
        self.addWidget(self.status_label, 0)
        self.addWidget(self.errors_label, 0)

    def set_file(self, path: str):
        self.file_label.setText(path)

    def set_status(self, text: str):
        self.status_label.setText(text)

    def set_errors(self, count: int):
        if count > 0:
            self.errors_label.setText(f"  {count} issue(s)  ")
            self.errors_label.setStyleSheet("color: #f44747; font-weight: bold; background: transparent;")
        else:
            self.errors_label.setText("  No issues  ")
            self.errors_label.setStyleSheet("color: #4ec9b0; background: transparent;")
