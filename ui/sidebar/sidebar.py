from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTabBar, QWidget


class Sidebar(QTabBar):
    page_changed = Signal(str)

    NAV_ITEMS = [
        ("general", "General"),
        ("advanced", "Advanced"),
        ("providers", "Providers"),
        ("models", "Models"),
        ("agents", "Agents"),
        ("mcp", "MCP"),
        ("editor", "Editor"),
        ("backups", "Backups"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setExpanding(False)
        self.setDrawBase(False)

        for key, label in self.NAV_ITEMS:
            self.addTab(label)
            tab_idx = self.count() - 1
            self.setTabData(tab_idx, key)

        self.currentChanged.connect(self._on_tab_changed)
        self.setCurrentIndex(0)

    def _on_tab_changed(self, index: int):
        if index >= 0:
            key = self.tabData(index)
            if key:
                self.page_changed.emit(key)

    def set_active(self, key: str):
        for i in range(self.count()):
            if self.tabData(i) == key:
                self.setCurrentIndex(i)
                break
