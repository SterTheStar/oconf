from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import ConfigManager
from ui.styles import VSCodeColors


class BackupsPanel(QWidget):
    config_changed = Signal()
    status_message = Signal(str)

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.cm = config_manager
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(16, 12, 16, 8)
        title = QLabel("Backups")
        title.setObjectName("sectionTitle")
        top_bar.addWidget(title)
        top_bar.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        top_bar.addWidget(refresh_btn)
        outer.addLayout(top_bar)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 4, 8, 12)
        left_layout.setSpacing(10)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["File", "Summary", "Size", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.currentCellChanged.connect(self._on_select)
        left_layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        restore_btn = QPushButton("Restore Selected")
        restore_btn.setObjectName("primaryBtn")
        restore_btn.setMinimumHeight(34)
        restore_btn.clicked.connect(self._restore)
        btn_row.addWidget(restore_btn)
        left_layout.addLayout(btn_row)

        content.addWidget(left, 1)

        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(8, 4, 16, 12)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Select a backup to preview its contents...")
        preview_layout.addWidget(self.preview, 1)

        content.addWidget(preview_container, 1)

        outer.addLayout(content)

    def _get_summary(self, path: Path) -> str:
        try:
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
        except (json.JSONDecodeError, OSError):
            return "Invalid JSON"

        parts = []
        providers = data.get("provider", {})
        if providers:
            total_models = sum(len(p.get("models", {})) for p in providers.values())
            parts.append(f"{len(providers)} providers, {total_models} models")

        agents = data.get("agent", {})
        if agents:
            parts.append(f"{len(agents)} agents")

        mcp = data.get("mcp", {})
        if mcp:
            parts.append(f"{len(mcp)} mcp")

        model = data.get("model", "")
        if model:
            parts.append(f"model: {model}")

        return " | ".join(parts) if parts else "Empty config"

    def _get_preview(self, path: Path) -> str:
        try:
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
        except (json.JSONDecodeError, OSError):
            return "Could not read backup file."

        lines = []

        model = data.get("model", "")
        small_model = data.get("small_model", "")
        if model:
            lines.append(f"Model: {model}")
        if small_model:
            lines.append(f"Small Model: {small_model}")

        providers = data.get("provider", {})
        if providers:
            lines.append(f"\n--- Providers ({len(providers)}) ---")
            for name, prov in providers.items():
                prov_name = prov.get("name", name)
                models = prov.get("models", {})
                base_url = prov.get("options", {}).get("baseURL", "")
                lines.append(f"  {name} ({prov_name}): {len(models)} models")
                if base_url:
                    lines.append(f"    URL: {base_url}")
                for mk in list(models.keys())[:5]:
                    lines.append(f"    - {mk}")
                if len(models) > 5:
                    lines.append(f"    ... +{len(models) - 5} more")

        agents = data.get("agent", {})
        if agents:
            lines.append(f"\n--- Agents ({len(agents)}) ---")
            for name, agent in agents.items():
                mode = agent.get("mode", "subagent")
                disabled = agent.get("disable", False)
                status = " [disabled]" if disabled else ""
                lines.append(f"  {name} ({mode}){status}")

        mcp = data.get("mcp", {})
        if mcp:
            lines.append(f"\n--- MCP Servers ({len(mcp)}) ---")
            for name, server in mcp.items():
                stype = server.get("type", "local")
                enabled = server.get("enabled", True)
                status = "" if enabled else " [disabled]"
                lines.append(f"  {name} ({stype}){status}")

        disabled = data.get("disabled_providers", [])
        if disabled:
            lines.append(f"\n--- Disabled Providers ---")
            lines.append(f"  {', '.join(disabled)}")

        return "\n".join(lines) if lines else "Empty config"

    def load_data(self):
        backups = self.cm.backup_manager.list_backups()
        self.table.setRowCount(len(backups))
        for row, bp in enumerate(backups):
            name_item = QTableWidgetItem(bp.name)
            name_item.setData(Qt.UserRole, str(bp))
            self.table.setItem(row, 0, name_item)

            summary = self._get_summary(bp)
            self.table.setItem(row, 1, QTableWidgetItem(summary))

            size = bp.stat().st_size
            if size > 1024:
                size_text = f"{size / 1024:.1f} KB"
            else:
                size_text = f"{size} B"
            self.table.setItem(row, 2, QTableWidgetItem(size_text))

            from datetime import datetime
            mtime = datetime.fromtimestamp(bp.stat().st_mtime)
            self.table.setItem(row, 3, QTableWidgetItem(mtime.strftime("%Y-%m-%d %H:%M:%S")))

        self.preview.setPlainText("")

    def _on_select(self, row, col, prev_row, prev_col):
        if row < 0:
            return
        name_item = self.table.item(row, 0)
        if name_item:
            bp_path = Path(name_item.data(Qt.UserRole))
            preview = self._get_preview(bp_path)
            self.preview.setPlainText(preview)

    def _restore(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Select a backup to restore.")
            return
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        bp_path = Path(name_item.data(Qt.UserRole))

        reply = QMessageBox.question(
            self, "Restore Backup",
            f"Restore from '{bp_path.name}'?\nA backup of the current file will be created first.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            if self.cm.backup_manager.restore_backup(bp_path):
                self.cm.load()
                self.load_data()
                self.config_changed.emit()
                self.status_message.emit(f"Restored from {bp_path.name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to restore backup.")
