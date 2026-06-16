from __future__ import annotations

import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import ConfigManager


class GeneralPanel(QWidget):
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
        title = QLabel("General Settings")
        title.setObjectName("sectionTitle")
        title_row.addWidget(title)
        title_row.addStretch()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save)
        title_row.addWidget(save_btn)
        layout.addLayout(title_row)

        schema_group = QGroupBox("Core")
        schema_form = QFormLayout(schema_group)
        schema_form.setSpacing(10)

        self.schema_edit = QLineEdit()
        self.schema_edit.setPlaceholderText("https://opencode.ai/config.json")
        schema_form.addRow("Schema URL:", self.schema_edit)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Optional display name")
        schema_form.addRow("Username:", self.username_edit)

        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("provider/model-id (e.g. anthropic/claude-sonnet-4-6)")
        schema_form.addRow("Default Model:", self.model_edit)

        self.small_model_edit = QLineEdit()
        self.small_model_edit.setPlaceholderText("provider/model-id for small tasks")
        schema_form.addRow("Small Model:", self.small_model_edit)

        self.default_agent_edit = QLineEdit()
        self.default_agent_edit.setPlaceholderText("e.g. build, plan, general")
        schema_form.addRow("Default Agent:", self.default_agent_edit)

        self.shell_edit = QLineEdit()
        self.shell_edit.setPlaceholderText("/bin/bash")
        schema_form.addRow("Shell:", self.shell_edit)

        layout.addWidget(schema_group)

        behavior_group = QGroupBox("Behavior")
        behavior_form = QFormLayout(behavior_group)
        behavior_form.setSpacing(10)

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARN", "ERROR"])
        behavior_form.addRow("Log Level:", self.log_level_combo)

        self.share_combo = QComboBox()
        self.share_combo.addItems(["manual", "auto", "disabled"])
        behavior_form.addRow("Share:", self.share_combo)

        self.autoupdate_combo = QComboBox()
        self.autoupdate_combo.addItems(["true", "false", "notify"])
        behavior_form.addRow("Auto Update:", self.autoupdate_combo)

        self.snapshot_check = QCheckBox("Enable snapshot tracking")
        behavior_form.addRow("Snapshot:", self.snapshot_check)

        layout.addWidget(behavior_group)

        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)

        self.instructions_edit = QLineEdit()
        self.instructions_edit.setPlaceholderText("Comma-separated instruction files (e.g. AGENTS.md, docs/style.md)")
        instructions_layout.addWidget(self.instructions_edit)

        layout.addWidget(instructions_group)

        disabled_group = QGroupBox("Disabled Providers")
        disabled_layout = QVBoxLayout(disabled_group)

        self.disabled_edit = QLineEdit()
        self.disabled_edit.setPlaceholderText("Comma-separated provider keys to disable")
        disabled_layout.addWidget(self.disabled_edit)

        layout.addWidget(disabled_group)

        enabled_group = QGroupBox("Enabled Providers (whitelist)")
        enabled_layout = QVBoxLayout(enabled_group)

        self.enabled_edit = QLineEdit()
        self.enabled_edit.setPlaceholderText("Comma-separated. If set, ONLY these providers are enabled")
        enabled_layout.addWidget(self.enabled_edit)

        layout.addWidget(enabled_group)

        layout.addStretch()
        scroll.setWidget(container)

    def load_data(self):
        cfg = self.cm.config
        self.schema_edit.setText(cfg.schema_url)
        self.username_edit.setText(cfg.username)
        self.model_edit.setText(cfg.model)
        self.small_model_edit.setText(cfg.small_model)
        self.default_agent_edit.setText(cfg.default_agent)
        self.shell_edit.setText(cfg.shell)

        idx = self.log_level_combo.findText(cfg.log_level)
        if idx >= 0:
            self.log_level_combo.setCurrentIndex(idx)

        idx = self.share_combo.findText(cfg.share)
        if idx >= 0:
            self.share_combo.setCurrentIndex(idx)

        au = str(cfg.autoupdate).lower()
        idx = self.autoupdate_combo.findText(au)
        if idx >= 0:
            self.autoupdate_combo.setCurrentIndex(idx)

        self.snapshot_check.setChecked(cfg.snapshot)
        self.instructions_edit.setText(", ".join(cfg.instructions))
        self.disabled_edit.setText(", ".join(cfg.disabled_providers))
        self.enabled_edit.setText(", ".join(cfg.enabled_providers))

    def _save(self):
        cfg = self.cm.config
        cfg.schema_url = self.schema_edit.text() or "https://opencode.ai/config.json"
        cfg.username = self.username_edit.text()
        cfg.model = self.model_edit.text()
        cfg.small_model = self.small_model_edit.text()
        cfg.default_agent = self.default_agent_edit.text()
        cfg.shell = self.shell_edit.text()
        cfg.log_level = self.log_level_combo.currentText()
        cfg.share = self.share_combo.currentText()

        au_text = self.autoupdate_combo.currentText()
        if au_text == "true":
            cfg.autoupdate = True
        elif au_text == "false":
            cfg.autoupdate = False
        else:
            cfg.autoupdate = "notify"

        cfg.snapshot = self.snapshot_check.isChecked()

        instr = self.instructions_edit.text().strip()
        cfg.instructions = [s.strip() for s in instr.split(",") if s.strip()] if instr else []

        dis = self.disabled_edit.text().strip()
        cfg.disabled_providers = [s.strip() for s in dis.split(",") if s.strip()] if dis else []

        ena = self.enabled_edit.text().strip()
        cfg.enabled_providers = [s.strip() for s in ena.split(",") if s.strip()] if ena else []

        self.cm.save()
        self.config_changed.emit()
