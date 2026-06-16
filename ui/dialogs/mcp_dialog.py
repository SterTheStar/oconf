from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.models import McpServerConfig


class McpDialog(QDialog):
    def __init__(self, server_name: str = "", server: McpServerConfig | None = None, parent=None):
        super().__init__(parent)
        self._server = server
        self._is_edit = server is not None
        self.setWindowTitle("Edit MCP Server" if self._is_edit else "Add MCP Server")
        self.setMinimumSize(560, 400)
        self.resize(600, 440)
        self._build_ui()
        if self._is_edit and server:
            self._load_data(server_name, server)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        tabs = QTabWidget()

        tab_basic = QWidget()
        tab_basic_layout = QVBoxLayout(tab_basic)
        tab_basic_layout.setContentsMargins(12, 12, 12, 12)

        basic_form = QFormLayout()
        basic_form.setSpacing(8)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. playwright, github")
        basic_form.addRow("Name:", self.name_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["local", "remote"])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        basic_form.addRow("Type:", self.type_combo)

        self.enabled_check = QCheckBox("Enabled")
        basic_form.addRow("Status:", self.enabled_check)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(0, 300000)
        self.timeout_spin.setSpecialValueText("Default (5000ms)")
        self.timeout_spin.setSuffix(" ms")
        basic_form.addRow("Timeout:", self.timeout_spin)

        tab_basic_layout.addLayout(basic_form)
        tab_basic_layout.addStretch()
        tabs.addTab(tab_basic, "Basic")

        tab_local = QWidget()
        tab_local_layout = QVBoxLayout(tab_local)
        tab_local_layout.setContentsMargins(12, 12, 12, 12)

        local_form = QFormLayout()
        local_form.setSpacing(8)

        self.command_edit = QLineEdit()
        self.command_edit.setPlaceholderText("e.g. npx -y @playwright/mcp")
        local_form.addRow("Command:", self.command_edit)

        self.cwd_edit = QLineEdit()
        self.cwd_edit.setPlaceholderText("Working directory (optional)")
        local_form.addRow("CWD:", self.cwd_edit)

        self.env_edit = QTextEdit()
        self.env_edit.setPlaceholderText('{"KEY": "value"}')
        self.env_edit.setMaximumHeight(100)
        local_form.addRow("Environment:", self.env_edit)

        tab_local_layout.addLayout(local_form)
        tab_local_layout.addStretch()
        self.tab_local = tab_local
        tabs.addTab(tab_local, "Local")

        tab_remote = QWidget()
        tab_remote_layout = QVBoxLayout(tab_remote)
        tab_remote_layout.setContentsMargins(12, 12, 12, 12)

        remote_form = QFormLayout()
        remote_form.setSpacing(8)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com/mcp")
        remote_form.addRow("URL:", self.url_edit)

        self.headers_edit = QTextEdit()
        self.headers_edit.setPlaceholderText('{"Authorization": "Bearer ..."}')
        self.headers_edit.setMaximumHeight(100)
        remote_form.addRow("Headers:", self.headers_edit)

        tab_remote_layout.addLayout(remote_form)
        tab_remote_layout.addStretch()
        self.tab_remote = tab_remote
        tabs.addTab(tab_remote, "Remote")

        self._tabs = tabs
        layout.addWidget(tabs, 1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        self._on_type_changed()

    def _on_type_changed(self):
        is_local = self.type_combo.currentText() == "local"
        idx_local = self._tabs.indexOf(self.tab_local)
        idx_remote = self._tabs.indexOf(self.tab_remote)
        if is_local:
            self._tabs.setTabVisible(idx_local, True)
            self._tabs.setTabVisible(idx_remote, False)
        else:
            self._tabs.setTabVisible(idx_local, False)
            self._tabs.setTabVisible(idx_remote, True)

    def _load_data(self, name: str, s: McpServerConfig):
        self.name_edit.setText(name)
        idx = self.type_combo.findText(s.server_type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        self.enabled_check.setChecked(s.enabled)
        self.command_edit.setText(" ".join(s.command))
        self.cwd_edit.setText(s.cwd)
        if s.env:
            self.env_edit.setPlainText(json.dumps(s.env, indent=2))
        self.url_edit.setText(s.url)
        if s.headers:
            self.headers_edit.setPlainText(json.dumps(s.headers, indent=2))
        if s.timeout is not None:
            self.timeout_spin.setValue(s.timeout)

    def get_server(self) -> tuple[str, McpServerConfig]:
        env = {}
        env_text = self.env_edit.toPlainText().strip()
        if env_text:
            try:
                env = json.loads(env_text)
            except json.JSONDecodeError:
                env = {}

        headers = {}
        headers_text = self.headers_edit.toPlainText().strip()
        if headers_text:
            try:
                headers = json.loads(headers_text)
            except json.JSONDecodeError:
                headers = {}

        command = [c.strip() for c in self.command_edit.text().split() if c.strip()]
        timeout = self.timeout_spin.value() if self.timeout_spin.value() > 0 else None

        return self.name_edit.text().strip(), McpServerConfig(
            name=self.name_edit.text().strip(),
            server_type=self.type_combo.currentText(),
            command=command,
            url=self.url_edit.text().strip(),
            enabled=self.enabled_check.isChecked(),
            env=env,
            headers=headers,
            cwd=self.cwd_edit.text().strip(),
            timeout=timeout,
        )
