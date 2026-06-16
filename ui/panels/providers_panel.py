from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import ConfigManager
from core.models import ProviderConfig
from services.provider_service import ProviderService
from ui.dialogs.provider_dialog import ProviderDialog
from ui.styles import VSCodeColors


class ProviderDetailPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        self.title_label = QLabel("Select a provider")
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.info_label = QLabel("")
        self.info_label.setObjectName("subtitleLabel")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.models_label = QLabel("")
        self.models_label.setWordWrap(True)
        layout.addWidget(self.models_label)

        layout.addStretch()

    def show_provider(self, key: str, provider: ProviderConfig):
        self.title_label.setText(f"{provider.name} ({key})")
        info_lines = []
        if provider.npm:
            info_lines.append(f"NPM: {provider.npm}")
        if provider.options.base_url:
            info_lines.append(f"Base URL: {provider.options.base_url}")
        if provider.options.api_key:
            info_lines.append(f"API Key: {'*' * 8}{provider.options.api_key[-4:]}" if len(provider.options.api_key) > 4 else "API Key: ****")
        if provider.env:
            info_lines.append(f"Env vars: {', '.join(provider.env)}")
        self.info_label.setText("\n".join(info_lines) if info_lines else "No additional configuration")

        if provider.models:
            model_lines = [f"  - {mk}: {mv.name or mk}" for mk, mv in provider.models.items()]
            self.models_label.setText(f"Models ({len(provider.models)}):\n" + "\n".join(model_lines))
        else:
            self.models_label.setText("No models configured")

    def clear(self):
        self.title_label.setText("Select a provider")
        self.info_label.setText("")
        self.models_label.setText("")


class ProvidersPanel(QWidget):
    config_changed = Signal()

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.cm = config_manager
        self.provider_service = ProviderService(config_manager)
        self._selected_key: str | None = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 12, 8, 12)
        left_layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(8)
        title = QLabel("Providers")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ Add Provider")
        add_btn.setObjectName("primaryBtn")
        add_btn.setMinimumHeight(36)
        add_btn.clicked.connect(self._add_provider)
        header.addWidget(add_btn)
        left_layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Key", "Name", "Models", "Status"])
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

        edit_btn = QPushButton("Edit")
        edit_btn.setMinimumHeight(34)
        edit_btn.clicked.connect(self._edit_provider)
        btn_row.addWidget(edit_btn)

        toggle_btn = QPushButton("Enable / Disable")
        toggle_btn.setMinimumHeight(34)
        toggle_btn.clicked.connect(self._toggle_provider)
        btn_row.addWidget(toggle_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.setMinimumHeight(34)
        delete_btn.clicked.connect(self._delete_provider)
        btn_row.addWidget(delete_btn)
        left_layout.addLayout(btn_row)

        content.addWidget(left, 1)

        self.detail = ProviderDetailPanel()
        self.detail.setFixedWidth(380)
        content.addWidget(self.detail)

        outer.addLayout(content)

    def load_data(self, select_row: int | None = None):
        providers = self.provider_service.get_all()
        self.table.setRowCount(len(providers))
        for row, (key, prov) in enumerate(providers.items()):
            key_item = QTableWidgetItem(key)
            key_item.setData(Qt.UserRole, key)
            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, QTableWidgetItem(prov.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(len(prov.models))))
            status = "Enabled" if self.provider_service.is_enabled(key) else "Disabled"
            self.table.setItem(row, 3, QTableWidgetItem(status))

        if select_row is not None and 0 <= select_row < self.table.rowCount():
            self.table.selectRow(select_row)
            self._on_select(select_row, 0, -1, -1)
        else:
            self.detail.clear()
            self._selected_key = None

    def _on_select(self, row, col, prev_row, prev_col):
        if row < 0:
            return
        key_item = self.table.item(row, 0)
        if key_item:
            key = key_item.data(Qt.UserRole)
            self._selected_key = key
            prov = self.provider_service.get(key)
            if prov:
                self.detail.show_provider(key, prov)

    def _add_provider(self):
        dlg = ProviderDialog(parent=self)
        if dlg.exec():
            provider = dlg.get_provider()
            if self.provider_service.add(provider):
                self.cm.save()
                self.load_data()
                self.config_changed.emit()
            else:
                QMessageBox.warning(self, "Error", f"Provider '{provider.key}' already exists.")

    def _edit_provider(self):
        if not self._selected_key:
            return
        prov = self.provider_service.get(self._selected_key)
        if not prov:
            return
        dlg = ProviderDialog(provider=prov, parent=self)
        if dlg.exec():
            updated = dlg.get_provider()
            if self.provider_service.update(self._selected_key, updated):
                self.cm.save()
                self.load_data()
                self.config_changed.emit()

    def _toggle_provider(self):
        if not self._selected_key:
            return
        self.provider_service.toggle_enabled(self._selected_key)
        self.cm.save()
        self.load_data()
        self.config_changed.emit()

    def _delete_provider(self):
        if not self._selected_key:
            return
        row = self.table.currentRow()
        reply = QMessageBox.question(
            self, "Delete Provider",
            f"Delete provider '{self._selected_key}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.provider_service.remove(self._selected_key)
            self.cm.save()
            next_row = min(row, self.table.rowCount() - 2)
            self.load_data(select_row=max(next_row, 0) if self.table.rowCount() > 0 else None)
            self.config_changed.emit()
