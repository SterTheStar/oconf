from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import ConfigManager
from ui.dialogs.provider_dialog import AgentDialog
from ui.panels.advanced_panel import AdvancedPanel
from ui.panels.agents_panel import AgentsPanel
from ui.panels.backups_panel import BackupsPanel
from ui.panels.editor_panel import EditorPanel
from ui.panels.general_panel import GeneralPanel
from ui.panels.mcp_panel import McpPanel
from ui.panels.models_panel import ModelsPanel
from ui.panels.providers_panel import ProvidersPanel
from ui.sidebar.sidebar import Sidebar
from ui.status_bar import StatusBar
from ui.styles import DARK_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OConf - OpenCode Configuration Manager")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        self.cm = ConfigManager()
        self.cm.load()

        self.menuBar().setVisible(False)
        self._bind_shortcuts()
        self._build_ui()
        self._load_all_panels()
        self._update_status()

    def _bind_shortcuts(self):
        save = QAction("Save", self)
        save.setShortcut(QKeySequence("Ctrl+S"))
        save.triggered.connect(self._save_config)
        self.addAction(save)

        reload = QAction("Reload", self)
        reload.setShortcut(QKeySequence("Ctrl+R"))
        reload.triggered.connect(self._reload_config)
        self.addAction(reload)

        validate = QAction("Validate", self)
        validate.setShortcut(QKeySequence("Ctrl+Shift+V"))
        validate.triggered.connect(self._validate_config)
        self.addAction(validate)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = Sidebar()
        self.tabs.page_changed.connect(self._on_page_changed)
        layout.addWidget(self.tabs)

        self.stack = QStackedWidget()
        self.general_panel = GeneralPanel(self.cm)
        self.advanced_panel = AdvancedPanel(self.cm)
        self.providers_panel = ProvidersPanel(self.cm)
        self.models_panel = ModelsPanel(self.cm)
        self.agents_panel = AgentsPanel(self.cm)
        self.mcp_panel = McpPanel(self.cm)
        self.editor_panel = EditorPanel(self.cm)
        self.backups_panel = BackupsPanel(self.cm)

        self.stack.addWidget(self.general_panel)
        self.stack.addWidget(self.advanced_panel)
        self.stack.addWidget(self.providers_panel)
        self.stack.addWidget(self.models_panel)
        self.stack.addWidget(self.agents_panel)
        self.stack.addWidget(self.mcp_panel)
        self.stack.addWidget(self.editor_panel)
        self.stack.addWidget(self.backups_panel)

        layout.addWidget(self.stack, 1)

        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        self.general_panel.config_changed.connect(self._on_config_changed)
        self.advanced_panel.config_changed.connect(self._on_config_changed)
        self.providers_panel.config_changed.connect(self._on_config_changed)
        self.models_panel.config_changed.connect(self._on_config_changed)
        self.agents_panel.config_changed.connect(self._on_config_changed)
        self.mcp_panel.config_changed.connect(self._on_config_changed)
        self.editor_panel.config_changed.connect(self._on_config_changed)
        self.editor_panel.status_message.connect(self.status_bar.set_status)
        self.backups_panel.config_changed.connect(self._on_config_changed)
        self.backups_panel.status_message.connect(self.status_bar.set_status)

    def _on_page_changed(self, key: str):
        page_map = {
            "general": 0,
            "advanced": 1,
            "providers": 2,
            "models": 3,
            "agents": 4,
            "mcp": 5,
            "editor": 6,
            "backups": 7,
        }
        idx = page_map.get(key, 0)
        self.stack.setCurrentIndex(idx)

    def _load_panel(self, key: str):
        if key == "general":
            self.general_panel.load_data()
        elif key == "advanced":
            self.advanced_panel.load_data()
        elif key == "providers":
            self.providers_panel.load_data()
        elif key == "models":
            self.models_panel.load_data()
        elif key == "agents":
            self.agents_panel.load_data()
        elif key == "mcp":
            self.mcp_panel.load_data()
        elif key == "editor":
            self.editor_panel.load_data()
        elif key == "backups":
            self.backups_panel.load_data()

    def _load_all_panels(self):
        self.general_panel.load_data()
        self.advanced_panel.load_data()
        self.providers_panel.load_data()
        self.models_panel.load_data()
        self.agents_panel.load_data()
        self.mcp_panel.load_data()
        self.editor_panel.load_data()
        self.backups_panel.load_data()

    def _on_config_changed(self):
        self._update_status()

    def _update_status(self):
        self.status_bar.set_file(str(self.cm.config_path))
        errors = self.cm.validate()
        self.status_bar.set_errors(len(errors))

    def _save_config(self):
        errors = self.cm.validate()
        if errors:
            reply = QMessageBox.warning(
                self, "Validation Issues",
                "Config has issues:\n" + "\n".join(errors[:5]) + "\n\nSave anyway?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
        self.cm.save()
        self.status_bar.set_status("Saved")
        QMessageBox.information(self, "Saved", "Configuration saved successfully.\nRestart opencode to apply changes.")

    def _reload_config(self):
        self.cm.load()
        self._load_all_panels()
        self._update_status()
        self.status_bar.set_status("Reloaded")

    def _validate_config(self):
        errors = self.cm.validate()
        if errors:
            QMessageBox.warning(
                self, "Validation",
                "Issues found:\n" + "\n".join(errors),
            )
        else:
            QMessageBox.information(self, "Validation", "Configuration is valid.")
