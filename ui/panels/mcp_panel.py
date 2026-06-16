from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import ConfigManager
from core.models import McpServerConfig
from ui.styles import VSCodeColors


class McpDetailPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        self.title_label = QLabel("Select an MCP server")
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.info_label = QLabel("")
        self.info_label.setObjectName("subtitleLabel")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        layout.addStretch()

    def show_server(self, name: str, server: McpServerConfig):
        self.title_label.setText(name)
        lines = [f"Type: {server.server_type}"]
        if server.server_type == "local":
            lines.append(f"Command: {' '.join(server.command)}")
            if server.cwd:
                lines.append(f"CWD: {server.cwd}")
            if server.env:
                lines.append(f"Environment: {server.env}")
        else:
            lines.append(f"URL: {server.url}")
            if server.headers:
                lines.append(f"Headers: {list(server.headers.keys())}")
        lines.append(f"Enabled: {'Yes' if server.enabled else 'No'}")
        if server.timeout is not None:
            lines.append(f"Timeout: {server.timeout}ms")
        self.info_label.setText("\n".join(lines))

    def clear(self):
        self.title_label.setText("Select an MCP server")
        self.info_label.setText("")


class McpPanel(QWidget):
    config_changed = Signal()

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.cm = config_manager
        self._selected_server: str | None = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 12, 8, 12)
        left_layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(8)
        title = QLabel("MCP Servers")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ Add Server")
        add_btn.setObjectName("primaryBtn")
        add_btn.setMinimumHeight(36)
        add_btn.clicked.connect(self._add_server)
        header.addWidget(add_btn)
        left_layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Enabled"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.currentCellChanged.connect(self._on_select)
        left_layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        edit_btn = QPushButton("Edit")
        edit_btn.setMinimumHeight(34)
        edit_btn.clicked.connect(self._edit_server)
        btn_row.addWidget(edit_btn)

        toggle_btn = QPushButton("Enable / Disable")
        toggle_btn.setMinimumHeight(34)
        toggle_btn.clicked.connect(self._toggle_server)
        btn_row.addWidget(toggle_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.setMinimumHeight(34)
        delete_btn.clicked.connect(self._delete_server)
        btn_row.addWidget(delete_btn)
        left_layout.addLayout(btn_row)

        content.addWidget(left, 1)

        self.detail = McpDetailPanel()
        self.detail.setFixedWidth(380)
        content.addWidget(self.detail)

        outer.addLayout(content)

    def load_data(self):
        servers = self.cm.config.mcp_servers
        self.table.setRowCount(len(servers))
        for row, (name, server) in enumerate(servers.items()):
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, name)
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, QTableWidgetItem(server.server_type))
            self.table.setItem(row, 2, QTableWidgetItem("Yes" if server.enabled else "No"))
        self.detail.clear()
        self._selected_server = None

    def _on_select(self, row, col, prev_row, prev_col):
        if row < 0:
            return
        name_item = self.table.item(row, 0)
        if name_item:
            name = name_item.data(Qt.UserRole)
            self._selected_server = name
            server = self.cm.config.mcp_servers.get(name)
            if server:
                self.detail.show_server(name, server)

    def _add_server(self):
        from ui.dialogs.mcp_dialog import McpDialog
        dlg = McpDialog(parent=self)
        if dlg.exec():
            name, server = dlg.get_server()
            if name in self.cm.config.mcp_servers:
                QMessageBox.warning(self, "Error", f"Server '{name}' already exists.")
                return
            self.cm.config.mcp_servers[name] = server
            self.cm.save()
            self.load_data()
            self.config_changed.emit()

    def _edit_server(self):
        if not self._selected_server:
            return
        server = self.cm.config.mcp_servers.get(self._selected_server)
        if not server:
            return
        from ui.dialogs.mcp_dialog import McpDialog
        dlg = McpDialog(server_name=self._selected_server, server=server, parent=self)
        if dlg.exec():
            new_name, updated = dlg.get_server()
            if new_name != self._selected_server:
                del self.cm.config.mcp_servers[self._selected_server]
            self.cm.config.mcp_servers[new_name] = updated
            self.cm.save()
            self.load_data()
            self.config_changed.emit()

    def _toggle_server(self):
        if not self._selected_server:
            return
        server = self.cm.config.mcp_servers.get(self._selected_server)
        if server:
            server.enabled = not server.enabled
            self.cm.save()
            self.load_data()
            self.config_changed.emit()

    def _delete_server(self):
        if not self._selected_server:
            return
        reply = QMessageBox.question(
            self, "Delete Server",
            f"Delete MCP server '{self._selected_server}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            del self.cm.config.mcp_servers[self._selected_server]
            self.cm.save()
            self.load_data()
            self.config_changed.emit()
