from __future__ import annotations

import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import ConfigManager


class JsonEdit(QTextEdit):
    def __init__(self, placeholder: str = "{}", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMaximumHeight(100)


class AdvancedPanel(QWidget):
    config_changed = Signal()

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.cm = config_manager
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title = QLabel("Advanced Settings")
        title.setObjectName("sectionTitle")
        title_row.addWidget(title)
        title_row.addStretch()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save)
        title_row.addWidget(save_btn)
        layout.addLayout(title_row)

        server_group = QGroupBox("Server")
        server_form = QFormLayout(server_group)
        server_form.setSpacing(8)

        self.server_port_spin = QSpinBox()
        self.server_port_spin.setRange(0, 65535)
        self.server_port_spin.setSpecialValueText("Default")
        server_form.addRow("Port:", self.server_port_spin)

        self.server_hostname_edit = QLineEdit()
        self.server_hostname_edit.setPlaceholderText("e.g. 127.0.0.1")
        server_form.addRow("Hostname:", self.server_hostname_edit)

        self.server_mdns_check = QCheckBox("Enable mDNS")
        server_form.addRow("mDNS:", self.server_mdns_check)

        self.server_mdns_domain_edit = QLineEdit()
        self.server_mdns_domain_edit.setPlaceholderText("opencode.local")
        server_form.addRow("mDNS Domain:", self.server_mdns_domain_edit)

        self.server_cors_edit = QLineEdit()
        self.server_cors_edit.setPlaceholderText("Comma-separated CORS origins")
        server_form.addRow("CORS:", self.server_cors_edit)

        layout.addWidget(server_group)

        compaction_group = QGroupBox("Compaction")
        comp_form = QFormLayout(compaction_group)
        comp_form.setSpacing(8)

        self.compaction_auto_check = QCheckBox("Auto-compact when context is full")
        comp_form.addRow("Auto:", self.compaction_auto_check)

        self.compaction_prune_check = QCheckBox("Prune old tool outputs")
        comp_form.addRow("Prune:", self.compaction_prune_check)

        self.compaction_tail_spin = QSpinBox()
        self.compaction_tail_spin.setRange(0, 100)
        self.compaction_tail_spin.setSpecialValueText("Default (2)")
        comp_form.addRow("Tail Turns:", self.compaction_tail_spin)

        self.compaction_reserved_spin = QSpinBox()
        self.compaction_reserved_spin.setRange(0, 100000)
        self.compaction_reserved_spin.setSpecialValueText("Default")
        self.compaction_reserved_spin.setSuffix(" tokens")
        comp_form.addRow("Reserved:", self.compaction_reserved_spin)

        layout.addWidget(compaction_group)

        permission_group = QGroupBox("Permissions (JSON)")
        perm_layout = QVBoxLayout(permission_group)
        self.permission_edit = JsonEdit('{"edit": "ask", "bash": {"git *": "allow"}}')
        perm_layout.addWidget(self.permission_edit)
        layout.addWidget(permission_group)

        tools_group = QGroupBox("Tools (enable/disable)")
        tools_layout = QVBoxLayout(tools_group)
        self.tools_edit = JsonEdit('{"webfetch": true, "websearch": false}')
        tools_layout.addWidget(self.tools_edit)
        layout.addWidget(tools_group)

        experimental_group = QGroupBox("Experimental (JSON)")
        exp_layout = QVBoxLayout(experimental_group)
        self.experimental_edit = JsonEdit('{"batch_tool": false, "mcp_timeout": 30000}')
        exp_layout.addWidget(self.experimental_edit)
        layout.addWidget(experimental_group)

        command_group = QGroupBox("Commands (JSON)")
        cmd_layout = QVBoxLayout(command_group)
        self.command_edit = JsonEdit('{"deploy": {"description": "...", "template": "..."}}')
        cmd_layout.addWidget(self.command_edit)
        layout.addWidget(command_group)

        skills_group = QGroupBox("Skills")
        skills_form = QFormLayout(skills_group)
        skills_form.setSpacing(8)

        self.skills_paths_edit = QLineEdit()
        self.skills_paths_edit.setPlaceholderText("Comma-separated skill folder paths")
        skills_form.addRow("Paths:", self.skills_paths_edit)

        self.skills_urls_edit = QLineEdit()
        self.skills_urls_edit.setPlaceholderText("Comma-separated skill URLs")
        skills_form.addRow("URLs:", self.skills_urls_edit)

        layout.addWidget(skills_group)

        references_group = QGroupBox("References (JSON)")
        ref_layout = QVBoxLayout(references_group)
        self.references_edit = JsonEdit('{"docs": {"path": "../docs", "description": "..."}}')
        ref_layout.addWidget(self.references_edit)
        layout.addWidget(references_group)

        plugin_group = QGroupBox("Plugins")
        plugin_layout = QVBoxLayout(plugin_group)
        self.plugin_edit = QLineEdit()
        self.plugin_edit.setPlaceholderText("Comma-separated plugin names or paths")
        plugin_layout.addWidget(self.plugin_edit)
        layout.addWidget(plugin_group)

        attachment_group = QGroupBox("Attachment Settings")
        att_form = QFormLayout(attachment_group)
        att_form.setSpacing(8)

        self.attachment_auto_resize_check = QCheckBox("Auto-resize images")
        att_form.addRow("Auto Resize:", self.attachment_auto_resize_check)

        self.attachment_max_width_spin = QSpinBox()
        self.attachment_max_width_spin.setRange(0, 10000)
        self.attachment_max_width_spin.setSpecialValueText("Default (2000)")
        self.attachment_max_width_spin.setSuffix(" px")
        att_form.addRow("Max Width:", self.attachment_max_width_spin)

        self.attachment_max_height_spin = QSpinBox()
        self.attachment_max_height_spin.setRange(0, 10000)
        self.attachment_max_height_spin.setSpecialValueText("Default (2000)")
        self.attachment_max_height_spin.setSuffix(" px")
        att_form.addRow("Max Height:", self.attachment_max_height_spin)

        layout.addWidget(attachment_group)

        tool_output_group = QGroupBox("Tool Output Limits")
        to_form = QFormLayout(tool_output_group)
        to_form.setSpacing(8)

        self.tool_output_max_lines_spin = QSpinBox()
        self.tool_output_max_lines_spin.setRange(0, 100000)
        self.tool_output_max_lines_spin.setSpecialValueText("Default (2000)")
        to_form.addRow("Max Lines:", self.tool_output_max_lines_spin)

        self.tool_output_max_bytes_spin = QSpinBox()
        self.tool_output_max_bytes_spin.setRange(0, 10_000_000)
        self.tool_output_max_bytes_spin.setSpecialValueText("Default (51200)")
        self.tool_output_max_bytes_spin.setSuffix(" bytes")
        to_form.addRow("Max Bytes:", self.tool_output_max_bytes_spin)

        layout.addWidget(tool_output_group)

        enterprise_group = QGroupBox("Enterprise")
        ent_form = QFormLayout(enterprise_group)
        ent_form.setSpacing(8)

        self.enterprise_url_edit = QLineEdit()
        self.enterprise_url_edit.setPlaceholderText("GitHub Enterprise URL")
        ent_form.addRow("URL:", self.enterprise_url_edit)

        layout.addWidget(enterprise_group)

        watcher_group = QGroupBox("Watcher")
        watch_layout = QVBoxLayout(watcher_group)
        self.watcher_edit = JsonEdit('{"ignore": [".git", "node_modules"]}')
        watch_layout.addWidget(self.watcher_edit)
        layout.addWidget(watcher_group)

        lsp_group = QGroupBox("LSP")
        lsp_layout = QVBoxLayout(lsp_group)
        self.lsp_edit = JsonEdit('true or {"command": ["..."], "extensions": [".ts"]}')
        lsp_layout.addWidget(self.lsp_edit)
        layout.addWidget(lsp_group)

        formatter_group = QGroupBox("Formatter")
        fmt_layout = QVBoxLayout(formatter_group)
        self.formatter_edit = JsonEdit('true or {"command": ["prettier", "--write"]}')
        fmt_layout.addWidget(self.formatter_edit)
        layout.addWidget(formatter_group)

        layout.addStretch()
        scroll.setWidget(container)

    def load_data(self):
        cfg = self.cm.config

        server = cfg.server
        self.server_port_spin.setValue(server.get("port", 0))
        self.server_hostname_edit.setText(server.get("hostname", ""))
        self.server_mdns_check.setChecked(server.get("mdns", False))
        self.server_mdns_domain_edit.setText(server.get("mdnsDomain", ""))
        self.server_cors_edit.setText(", ".join(server.get("cors", [])))

        comp = cfg.compaction
        self.compaction_auto_check.setChecked(comp.get("auto", True))
        self.compaction_prune_check.setChecked(comp.get("prune", False))
        self.compaction_tail_spin.setValue(comp.get("tail_turns", 0))
        self.compaction_reserved_spin.setValue(comp.get("reserved", 0))

        if cfg.permission:
            self.permission_edit.setPlainText(json.dumps(cfg.permission, indent=2))
        if cfg.tools:
            self.tools_edit.setPlainText(json.dumps(cfg.tools, indent=2))
        if cfg.experimental:
            self.experimental_edit.setPlainText(json.dumps(cfg.experimental, indent=2))
        if cfg.command:
            self.command_edit.setPlainText(json.dumps(cfg.command, indent=2))

        skills = cfg.skills
        self.skills_paths_edit.setText(", ".join(skills.get("paths", [])))
        self.skills_urls_edit.setText(", ".join(skills.get("urls", [])))

        if cfg.references:
            self.references_edit.setPlainText(json.dumps(cfg.references, indent=2))

        if cfg.plugin:
            plugin_strs = []
            for p in cfg.plugin:
                if isinstance(p, list):
                    plugin_strs.append(json.dumps(p))
                else:
                    plugin_strs.append(str(p))
            self.plugin_edit.setText(", ".join(plugin_strs))

        att = cfg.attachment
        img = att.get("image", {})
        self.attachment_auto_resize_check.setChecked(img.get("auto_resize", True))
        self.attachment_max_width_spin.setValue(img.get("max_width", 0))
        self.attachment_max_height_spin.setValue(img.get("max_height", 0))

        to = cfg.tool_output
        self.tool_output_max_lines_spin.setValue(to.get("max_lines", 0))
        self.tool_output_max_bytes_spin.setValue(to.get("max_bytes", 0))

        self.enterprise_url_edit.setText(cfg.enterprise.get("url", ""))

        if cfg.watcher:
            self.watcher_edit.setPlainText(json.dumps(cfg.watcher, indent=2))
        if cfg.lsp is not None:
            if isinstance(cfg.lsp, bool):
                self.lsp_edit.setPlainText("true" if cfg.lsp else "false")
            else:
                self.lsp_edit.setPlainText(json.dumps(cfg.lsp, indent=2))
        if cfg.formatter is not None:
            if isinstance(cfg.formatter, bool):
                self.formatter_edit.setPlainText("true" if cfg.formatter else "false")
            else:
                self.formatter_edit.setPlainText(json.dumps(cfg.formatter, indent=2))

    def _save(self):
        cfg = self.cm.config

        server = {}
        if self.server_port_spin.value() > 0:
            server["port"] = self.server_port_spin.value()
        if self.server_hostname_edit.text().strip():
            server["hostname"] = self.server_hostname_edit.text().strip()
        if self.server_mdns_check.isChecked():
            server["mdns"] = True
        if self.server_mdns_domain_edit.text().strip():
            server["mdnsDomain"] = self.server_mdns_domain_edit.text().strip()
        cors = [s.strip() for s in self.server_cors_edit.text().split(",") if s.strip()]
        if cors:
            server["cors"] = cors
        cfg.server = server

        comp = {}
        if not self.compaction_auto_check.isChecked():
            comp["auto"] = False
        if self.compaction_prune_check.isChecked():
            comp["prune"] = True
        if self.compaction_tail_spin.value() > 0:
            comp["tail_turns"] = self.compaction_tail_spin.value()
        if self.compaction_reserved_spin.value() > 0:
            comp["reserved"] = self.compaction_reserved_spin.value()
        cfg.compaction = comp

        cfg.permission = self._parse_json(self.permission_edit)
        cfg.tools = self._parse_json(self.tools_edit)
        cfg.experimental = self._parse_json(self.experimental_edit)
        cfg.command = self._parse_json(self.command_edit)

        skills = {}
        paths = [s.strip() for s in self.skills_paths_edit.text().split(",") if s.strip()]
        urls = [s.strip() for s in self.skills_urls_edit.text().split(",") if s.strip()]
        if paths:
            skills["paths"] = paths
        if urls:
            skills["urls"] = urls
        cfg.skills = skills

        cfg.references = self._parse_json(self.references_edit)

        plugin_text = self.plugin_edit.text().strip()
        if plugin_text:
            cfg.plugin = [s.strip() for s in plugin_text.split(",") if s.strip()]
        else:
            cfg.plugin = []

        img = {}
        if not self.attachment_auto_resize_check.isChecked():
            img["auto_resize"] = False
        if self.attachment_max_width_spin.value() > 0:
            img["max_width"] = self.attachment_max_width_spin.value()
        if self.attachment_max_height_spin.value() > 0:
            img["max_height"] = self.attachment_max_height_spin.value()
        cfg.attachment = {"image": img} if img else {}

        to = {}
        if self.tool_output_max_lines_spin.value() > 0:
            to["max_lines"] = self.tool_output_max_lines_spin.value()
        if self.tool_output_max_bytes_spin.value() > 0:
            to["max_bytes"] = self.tool_output_max_bytes_spin.value()
        cfg.tool_output = to

        ent = {}
        if self.enterprise_url_edit.text().strip():
            ent["url"] = self.enterprise_url_edit.text().strip()
        cfg.enterprise = ent

        cfg.watcher = self._parse_json(self.watcher_edit)

        lsp_text = self.lsp_edit.toPlainText().strip()
        if lsp_text == "true":
            cfg.lsp = True
        elif lsp_text == "false":
            cfg.lsp = False
        else:
            cfg.lsp = self._parse_json(self.lsp_edit) or None

        fmt_text = self.formatter_edit.toPlainText().strip()
        if fmt_text == "true":
            cfg.formatter = True
        elif fmt_text == "false":
            cfg.formatter = False
        else:
            cfg.formatter = self._parse_json(self.formatter_edit) or None

        self.cm.save()
        self.config_changed.emit()

    def _parse_json(self, widget: QTextEdit):
        text = widget.toPlainText().strip()
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}
