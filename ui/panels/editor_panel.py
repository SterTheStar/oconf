from __future__ import annotations

import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import ConfigManager
from ui.styles import VSCodeColors


class EditorPanel(QWidget):
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

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(16, 12, 16, 8)
        toolbar.setSpacing(8)

        title = QLabel("Raw Editor")
        title.setObjectName("sectionTitle")
        toolbar.addWidget(title)
        toolbar.addStretch()

        validate_btn = QPushButton("Validate")
        validate_btn.clicked.connect(self._validate)
        toolbar.addWidget(validate_btn)

        format_btn = QPushButton("Format")
        format_btn.clicked.connect(self._format)
        toolbar.addWidget(format_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("primaryBtn")
        apply_btn.clicked.connect(self._apply)
        toolbar.addWidget(apply_btn)

        reload_btn = QPushButton("Reload")
        reload_btn.clicked.connect(self._reload)
        toolbar.addWidget(reload_btn)

        outer.addLayout(toolbar)

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(16, 0, 16, 12)

        self.editor = QPlainTextEdit()
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.editor.setTabStopDistance(4)
        font = self.editor.font()
        font.setFamily("Cascadia Code, Fira Code, Consolas, monospace")
        font.setPointSize(12)
        self.editor.setFont(font)
        editor_layout.addWidget(self.editor, 1)

        outer.addWidget(editor_container, 1)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {VSCodeColors.FG_ERROR}; padding: 4px 12px;")
        self.error_label.setVisible(False)
        outer.addWidget(self.error_label)

    def load_data(self):
        path = self.cm.config_path
        if path.exists():
            text = path.read_text(encoding="utf-8")
            self.editor.setPlainText(text)
        else:
            self.editor.setPlainText("{\n  \"$schema\": \"https://opencode.ai/config.json\"\n}")
        self.error_label.setVisible(False)

    def _validate(self):
        text = self.editor.toPlainText()
        errors = self.cm.apply_raw_json(text)
        if errors:
            self.error_label.setText(" | ".join(errors))
            self.error_label.setVisible(True)
            self.status_message.emit("Validation failed")
        else:
            self.error_label.setText("Valid JSON")
            self.error_label.setStyleSheet(f"color: {VSCodeColors.FG_SUCCESS}; padding: 4px 12px;")
            self.error_label.setVisible(True)
            self.status_message.emit("Validation passed")

    def _format(self):
        text = self.editor.toPlainText()
        try:
            stripped = self.cm._strip_comments(text)
            stripped = self.cm._strip_trailing_commas(stripped)
            data = json.loads(stripped)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self.editor.setPlainText(formatted)
            self.error_label.setVisible(False)
            self.status_message.emit("Formatted")
        except json.JSONDecodeError as e:
            self.error_label.setText(f"Cannot format: {e}")
            self.error_label.setStyleSheet(f"color: {VSCodeColors.FG_ERROR}; padding: 4px 12px;")
            self.error_label.setVisible(True)

    def _apply(self):
        text = self.editor.toPlainText()
        errors = self.cm.apply_raw_json(text)
        if errors:
            reply = QMessageBox.warning(
                self, "Validation Errors",
                "The JSON has errors:\n" + "\n".join(errors) + "\n\nSave anyway?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
        self.cm.save()
        self.error_label.setVisible(False)
        self.status_message.emit("Saved")

    def _reload(self):
        self.load_data()
        self.status_message.emit("Reloaded from disk")
