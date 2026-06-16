from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import ConfigManager
from core.models import ModelConfig, ProviderConfig
from services.model_fetcher import add_models_from_api
from services.model_service import ModelService
from services.provider_service import ProviderService
from ui.dialogs.model_dialog import ModelDialog
from ui.styles import VSCodeColors


class ModelsPanel(QWidget):
    config_changed = Signal()

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.cm = config_manager
        self.provider_service = ProviderService(config_manager)
        self.model_service = ModelService(config_manager)
        self._selected_provider: str | None = None
        self._selected_model: str | None = None
        self._disabled_models: set[str] = set()
        self._disabled_file = config_manager.config_path.parent / "disabled_models.json"
        self._load_disabled()
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(16, 12, 16, 8)
        top_bar.setSpacing(8)
        title = QLabel("Models")
        title.setObjectName("sectionTitle")
        top_bar.addWidget(title)
        top_bar.addStretch()

        top_bar.addWidget(QLabel("Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.setMinimumWidth(200)
        self.provider_combo.setMinimumHeight(34)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        top_bar.addWidget(self.provider_combo)

        fetch_btn = QPushButton("Fetch from API")
        fetch_btn.setMinimumHeight(36)
        fetch_btn.setToolTip("Query /v1/models and add missing models automatically")
        fetch_btn.clicked.connect(self._fetch_models)
        top_bar.addWidget(fetch_btn)

        add_btn = QPushButton("+ Add Model")
        add_btn.setObjectName("primaryBtn")
        add_btn.setMinimumHeight(36)
        add_btn.clicked.connect(self._add_model)
        top_bar.addWidget(add_btn)
        outer.addLayout(top_bar)

        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(16, 4, 16, 12)
        table_layout.setSpacing(10)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Key", "Name", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.currentCellChanged.connect(self._on_select)
        table_layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        edit_btn = QPushButton("Edit")
        edit_btn.setMinimumHeight(34)
        edit_btn.clicked.connect(self._edit_model)
        btn_row.addWidget(edit_btn)

        self.toggle_btn = QPushButton("Disable")
        self.toggle_btn.setMinimumHeight(34)
        self.toggle_btn.clicked.connect(self._toggle_model)
        btn_row.addWidget(self.toggle_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.setMinimumHeight(34)
        delete_btn.clicked.connect(self._delete_model)
        btn_row.addWidget(delete_btn)
        table_layout.addLayout(btn_row)

        outer.addWidget(table_container)

    def load_data(self):
        self.provider_combo.blockSignals(True)
        self.provider_combo.clear()
        providers = self.provider_service.get_all()
        self.provider_combo.addItem("-- Select Provider --", None)
        for key, prov in providers.items():
            self.provider_combo.addItem(f"{prov.name or key}", key)
        self.provider_combo.blockSignals(False)
        self._load_models()

    def _on_provider_changed(self, index):
        self._load_models()

    def _load_models(self, select_row: int | None = None):
        idx = self.provider_combo.currentIndex()
        if idx <= 0:
            self._selected_provider = None
            self.table.setRowCount(0)
            return
        self._selected_provider = self.provider_combo.currentData()
        models = self.model_service.get_models(self._selected_provider)
        self.table.setRowCount(len(models))
        for row, (mk, mv) in enumerate(models.items()):
            key_item = QTableWidgetItem(mk)
            key_item.setData(Qt.UserRole, mk)
            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, QTableWidgetItem(mv.name))
            full_key = f"{self._selected_provider}/{mk}"
            status = "Disabled" if full_key in self._disabled_models else (mv.status or "active")
            self.table.setItem(row, 2, QTableWidgetItem(status))

        if select_row is not None and 0 <= select_row < self.table.rowCount():
            self.table.selectRow(select_row)
            self._on_select(select_row, 0, -1, -1)
        else:
            self._selected_model = None
        self._update_toggle_btn()

    def _on_select(self, row, col, prev_row, prev_col):
        if row < 0 or not self._selected_provider:
            return
        key_item = self.table.item(row, 0)
        if key_item:
            mk = key_item.data(Qt.UserRole)
            self._selected_model = mk
        self._update_toggle_btn()

    def _update_toggle_btn(self):
        if not self._selected_provider or not self._selected_model:
            self.toggle_btn.setEnabled(False)
            return
        self.toggle_btn.setEnabled(True)
        full_key = f"{self._selected_provider}/{self._selected_model}"
        if full_key in self._disabled_models:
            self.toggle_btn.setText("Enable")
        else:
            self.toggle_btn.setText("Disable")

    def _toggle_model(self):
        if not self._selected_provider or not self._selected_model:
            return
        full_key = f"{self._selected_provider}/{self._selected_model}"
        if full_key in self._disabled_models:
            self._disabled_models.discard(full_key)
        else:
            self._disabled_models.add(full_key)
        self._save_disabled()
        row = self.table.currentRow()
        self._load_models(select_row=row if row >= 0 else None)
        self.config_changed.emit()

    def _load_disabled(self):
        if self._disabled_file.exists():
            try:
                data = json.loads(self._disabled_file.read_text(encoding="utf-8"))
                self._disabled_models = set(data)
            except (json.JSONDecodeError, TypeError):
                self._disabled_models = set()

    def _save_disabled(self):
        self._disabled_file.write_text(
            json.dumps(sorted(self._disabled_models), indent=2),
            encoding="utf-8",
        )

    def _add_model(self):
        if not self._selected_provider:
            QMessageBox.information(self, "Info", "Select a provider first.")
            return
        dlg = ModelDialog(parent=self)
        if dlg.exec():
            model_key, model = dlg.get_model()
            if self.model_service.add_model(self._selected_provider, model_key, model):
                self.cm.save()
                self._load_models()
                self.config_changed.emit()
            else:
                QMessageBox.warning(self, "Error", f"Model '{model_key}' already exists in this provider.")

    def _edit_model(self):
        if not self._selected_provider or not self._selected_model:
            return
        model = self.model_service.get_model(self._selected_provider, self._selected_model)
        if not model:
            return
        dlg = ModelDialog(model_key=self._selected_model, model=model, parent=self)
        if dlg.exec():
            new_key, updated = dlg.get_model()
            updated.id = new_key
            if self.model_service.update_model(self._selected_provider, self._selected_model, new_key, updated):
                self.cm.save()
                self._load_models()
                self.config_changed.emit()

    def _delete_model(self):
        if not self._selected_provider or not self._selected_model:
            return
        row = self.table.currentRow()
        reply = QMessageBox.question(
            self, "Delete Model",
            f"Delete model '{self._selected_model}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.model_service.remove_model(self._selected_provider, self._selected_model)
            self.cm.save()
            next_row = min(row, self.table.rowCount() - 2)
            self._load_models(select_row=max(next_row, 0) if self.table.rowCount() > 0 else None)
            self.config_changed.emit()

    def _fetch_models(self):
        if not self._selected_provider:
            QMessageBox.information(self, "Info", "Select a provider first.")
            return

        prov = self.provider_service.get(self._selected_provider)
        if not prov:
            return

        if not prov.options.base_url:
            QMessageBox.warning(self, "Error", "This provider has no base URL configured.")
            return

        existing_keys = set(prov.models.keys())
        result = add_models_from_api(prov, existing_keys)

        if result.errors:
            QMessageBox.warning(self, "Fetch Error", "\n".join(result.errors))
            return

        if result.added == 0:
            QMessageBox.information(
                self, "Fetch Models",
                f"Found {result.total} model(s) on the API.\n"
                f"All {result.skipped} already exist. Nothing new added.",
            )
        else:
            self.cm.save()
            self._load_models()
            self.config_changed.emit()
            QMessageBox.information(
                self, "Fetch Models",
                f"Found {result.total} model(s) on the API.\n"
                f"Added: {result.added}  |  Skipped (already exist): {result.skipped}",
            )
