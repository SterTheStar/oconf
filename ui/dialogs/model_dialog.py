from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.models import ModelConfig, ModelCost, ModelLimit


class ModelDialog(QDialog):
    def __init__(self, model_key: str = "", model: ModelConfig | None = None, parent=None):
        super().__init__(parent)
        self._model = model
        self._is_edit = model is not None
        self.setWindowTitle("Edit Model" if self._is_edit else "Add Model")
        self.setMinimumSize(600, 480)
        self.resize(650, 520)
        self._build_ui()
        if self._is_edit and model:
            self._load_data(model_key, model)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        tabs = QTabWidget()

        tab_basic = QWidget()
        tab_basic_layout = QVBoxLayout(tab_basic)
        tab_basic_layout.setContentsMargins(12, 12, 12, 12)

        basic_form = QFormLayout()
        basic_form.setSpacing(8)

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Model ID (e.g. claude-sonnet-4-6)")
        basic_form.addRow("Key:", self.key_edit)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Display name")
        basic_form.addRow("Name:", self.name_edit)

        self.family_edit = QLineEdit()
        self.family_edit.setPlaceholderText("e.g. claude, gpt, gemini")
        basic_form.addRow("Family:", self.family_edit)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "beta", "alpha", "deprecated"])
        basic_form.addRow("Status:", self.status_combo)

        self.release_date_edit = QLineEdit()
        self.release_date_edit.setPlaceholderText("e.g. 2024-01-15")
        basic_form.addRow("Release Date:", self.release_date_edit)

        tab_basic_layout.addLayout(basic_form)

        caps_group = QGroupBox("Capabilities")
        caps_layout = QVBoxLayout(caps_group)
        self.attachment_check = QCheckBox("Attachment (file uploads)")
        caps_layout.addWidget(self.attachment_check)
        self.reasoning_check = QCheckBox("Reasoning (chain-of-thought)")
        caps_layout.addWidget(self.reasoning_check)
        self.temperature_check = QCheckBox("Temperature control")
        caps_layout.addWidget(self.temperature_check)
        self.tool_call_check = QCheckBox("Tool/function calling")
        caps_layout.addWidget(self.tool_call_check)
        self.experimental_check = QCheckBox("Experimental")
        caps_layout.addWidget(self.experimental_check)
        tab_basic_layout.addWidget(caps_group)

        tab_basic_layout.addStretch()
        tabs.addTab(tab_basic, "Basic")

        tab_limits = QWidget()
        tab_limits_layout = QVBoxLayout(tab_limits)
        tab_limits_layout.setContentsMargins(12, 12, 12, 12)

        limits_form = QFormLayout()
        limits_form.setSpacing(8)

        self.context_spin = QSpinBox()
        self.context_spin.setRange(0, 10_000_000)
        self.context_spin.setSuffix(" tokens")
        limits_form.addRow("Context window:", self.context_spin)

        self.input_spin = QSpinBox()
        self.input_spin.setRange(0, 10_000_000)
        self.input_spin.setSpecialValueText("Default")
        self.input_spin.setSuffix(" tokens")
        limits_form.addRow("Max input:", self.input_spin)

        self.output_spin = QSpinBox()
        self.output_spin.setRange(0, 10_000_000)
        self.output_spin.setSuffix(" tokens")
        limits_form.addRow("Max output:", self.output_spin)

        tab_limits_layout.addLayout(limits_form)

        mod_group = QGroupBox("Modalities")
        mod_form = QFormLayout(mod_group)
        mod_form.setSpacing(8)
        self.input_modalities_edit = QLineEdit()
        self.input_modalities_edit.setPlaceholderText("Comma-separated: text, audio, image, video, pdf")
        mod_form.addRow("Input:", self.input_modalities_edit)
        self.output_modalities_edit = QLineEdit()
        self.output_modalities_edit.setPlaceholderText("Comma-separated: text, audio, image, video, pdf")
        mod_form.addRow("Output:", self.output_modalities_edit)
        tab_limits_layout.addWidget(mod_group)

        tab_limits_layout.addStretch()
        tabs.addTab(tab_limits, "Limits")

        tab_cost = QWidget()
        tab_cost_layout = QVBoxLayout(tab_cost)
        tab_cost_layout.setContentsMargins(12, 12, 12, 12)

        cost_form = QFormLayout()
        cost_form.setSpacing(8)

        self.cost_input_spin = QDoubleSpinBox()
        self.cost_input_spin.setRange(0, 1000)
        self.cost_input_spin.setDecimals(4)
        self.cost_input_spin.setPrefix("$ ")
        cost_form.addRow("Input:", self.cost_input_spin)

        self.cost_output_spin = QDoubleSpinBox()
        self.cost_output_spin.setRange(0, 1000)
        self.cost_output_spin.setDecimals(4)
        self.cost_output_spin.setPrefix("$ ")
        cost_form.addRow("Output:", self.cost_output_spin)

        self.cost_cache_read_spin = QDoubleSpinBox()
        self.cost_cache_read_spin.setRange(0, 1000)
        self.cost_cache_read_spin.setDecimals(4)
        self.cost_cache_read_spin.setPrefix("$ ")
        cost_form.addRow("Cache read:", self.cost_cache_read_spin)

        self.cost_cache_write_spin = QDoubleSpinBox()
        self.cost_cache_write_spin.setRange(0, 1000)
        self.cost_cache_write_spin.setDecimals(4)
        self.cost_cache_write_spin.setPrefix("$ ")
        cost_form.addRow("Cache write:", self.cost_cache_write_spin)

        tab_cost_layout.addLayout(cost_form)

        over200k_group = QGroupBox("Cost Over 200k Context")
        over_form = QFormLayout(over200k_group)
        over_form.setSpacing(8)

        self.over200k_input_spin = QDoubleSpinBox()
        self.over200k_input_spin.setRange(0, 1000)
        self.over200k_input_spin.setDecimals(4)
        self.over200k_input_spin.setPrefix("$ ")
        over_form.addRow("Input:", self.over200k_input_spin)

        self.over200k_output_spin = QDoubleSpinBox()
        self.over200k_output_spin.setRange(0, 1000)
        self.over200k_output_spin.setDecimals(4)
        self.over200k_output_spin.setPrefix("$ ")
        over_form.addRow("Output:", self.over200k_output_spin)

        self.over200k_cache_read_spin = QDoubleSpinBox()
        self.over200k_cache_read_spin.setRange(0, 1000)
        self.over200k_cache_read_spin.setDecimals(4)
        self.over200k_cache_read_spin.setPrefix("$ ")
        over_form.addRow("Cache read:", self.over200k_cache_read_spin)

        self.over200k_cache_write_spin = QDoubleSpinBox()
        self.over200k_cache_write_spin.setRange(0, 1000)
        self.over200k_cache_write_spin.setDecimals(4)
        self.over200k_cache_write_spin.setPrefix("$ ")
        over_form.addRow("Cache write:", self.over200k_cache_write_spin)

        tab_cost_layout.addWidget(over200k_group)
        tab_cost_layout.addStretch()
        tabs.addTab(tab_cost, "Cost")

        tab_json = QWidget()
        tab_json_layout = QVBoxLayout(tab_json)
        tab_json_layout.setContentsMargins(12, 12, 12, 12)

        json_form = QFormLayout()
        json_form.setSpacing(8)

        self.headers_edit = QTextEdit()
        self.headers_edit.setPlaceholderText('{"Authorization": "Bearer ..."}')
        self.headers_edit.setMaximumHeight(80)
        json_form.addRow("Headers:", self.headers_edit)

        self.provider_override_edit = QTextEdit()
        self.provider_override_edit.setPlaceholderText('{"npm": "@ai-sdk/custom", "api": "custom"}')
        self.provider_override_edit.setMaximumHeight(80)
        json_form.addRow("Provider Overrides:", self.provider_override_edit)

        self.options_edit = QTextEdit()
        self.options_edit.setPlaceholderText('{"key": "value"}')
        self.options_edit.setMaximumHeight(80)
        json_form.addRow("Options:", self.options_edit)

        self.variants_edit = QTextEdit()
        self.variants_edit.setPlaceholderText('{"fast": {}, "quality": {"disabled": true}}')
        self.variants_edit.setMaximumHeight(80)
        json_form.addRow("Variants:", self.variants_edit)

        tab_json_layout.addLayout(json_form)
        tab_json_layout.addStretch()
        tabs.addTab(tab_json, "JSON")

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

    def _load_data(self, key: str, m: ModelConfig):
        self.key_edit.setText(key)
        self.name_edit.setText(m.name)
        self.family_edit.setText(m.family)
        idx = self.status_combo.findText(m.status or "active")
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)
        self.release_date_edit.setText(m.release_date)
        self.attachment_check.setChecked(m.attachment)
        self.reasoning_check.setChecked(m.reasoning)
        self.temperature_check.setChecked(m.temperature)
        self.tool_call_check.setChecked(m.tool_call)
        self.experimental_check.setChecked(m.experimental)
        if m.modalities:
            self.input_modalities_edit.setText(", ".join(m.modalities.get("input", [])))
            self.output_modalities_edit.setText(", ".join(m.modalities.get("output", [])))
        if m.limit:
            self.context_spin.setValue(m.limit.context)
            if m.limit.input is not None:
                self.input_spin.setValue(m.limit.input)
            self.output_spin.setValue(m.limit.output)
        if m.cost:
            self.cost_input_spin.setValue(m.cost.input)
            self.cost_output_spin.setValue(m.cost.output)
            if m.cost.cache_read is not None:
                self.cost_cache_read_spin.setValue(m.cost.cache_read)
            if m.cost.cache_write is not None:
                self.cost_cache_write_spin.setValue(m.cost.cache_write)
        if m.cost_context_over_200k:
            c = m.cost_context_over_200k
            self.over200k_input_spin.setValue(c.get("input", 0))
            self.over200k_output_spin.setValue(c.get("output", 0))
            if "cache_read" in c:
                self.over200k_cache_read_spin.setValue(c["cache_read"])
            if "cache_write" in c:
                self.over200k_cache_write_spin.setValue(c["cache_write"])
        if m.headers:
            self.headers_edit.setPlainText(json.dumps(m.headers, indent=2))
        if m.provider_override:
            self.provider_override_edit.setPlainText(json.dumps(m.provider_override, indent=2))
        if m.options:
            self.options_edit.setPlainText(json.dumps(m.options, indent=2))
        if m.variants:
            self.variants_edit.setPlainText(json.dumps(m.variants, indent=2))

    def get_model(self) -> tuple[str, ModelConfig]:
        options = {}
        opt_text = self.options_edit.toPlainText().strip()
        if opt_text:
            try:
                options = json.loads(opt_text)
            except json.JSONDecodeError:
                options = {}

        headers = {}
        headers_text = self.headers_edit.toPlainText().strip()
        if headers_text:
            try:
                headers = json.loads(headers_text)
            except json.JSONDecodeError:
                headers = {}

        provider_override = {}
        prov_text = self.provider_override_edit.toPlainText().strip()
        if prov_text:
            try:
                provider_override = json.loads(prov_text)
            except json.JSONDecodeError:
                provider_override = {}

        variants = {}
        var_text = self.variants_edit.toPlainText().strip()
        if var_text:
            try:
                variants = json.loads(var_text)
            except json.JSONDecodeError:
                variants = {}

        cost = None
        if self.cost_input_spin.value() > 0 or self.cost_output_spin.value() > 0:
            cost = ModelCost(
                input=self.cost_input_spin.value(),
                output=self.cost_output_spin.value(),
                cache_read=self.cost_cache_read_spin.value() if self.cost_cache_read_spin.value() > 0 else None,
                cache_write=self.cost_cache_write_spin.value() if self.cost_cache_write_spin.value() > 0 else None,
            )

        cost_over_200k = None
        if self.over200k_input_spin.value() > 0 or self.over200k_output_spin.value() > 0:
            cost_over_200k = {
                "input": self.over200k_input_spin.value(),
                "output": self.over200k_output_spin.value(),
            }
            if self.over200k_cache_read_spin.value() > 0:
                cost_over_200k["cache_read"] = self.over200k_cache_read_spin.value()
            if self.over200k_cache_write_spin.value() > 0:
                cost_over_200k["cache_write"] = self.over200k_cache_write_spin.value()

        limit = None
        if self.context_spin.value() > 0 or self.output_spin.value() > 0:
            limit = ModelLimit(
                context=self.context_spin.value(),
                input=self.input_spin.value() if self.input_spin.value() > 0 else None,
                output=self.output_spin.value(),
            )

        modalities = {}
        in_mod = self.input_modalities_edit.text().strip()
        out_mod = self.output_modalities_edit.text().strip()
        if in_mod:
            modalities["input"] = [s.strip() for s in in_mod.split(",") if s.strip()]
        if out_mod:
            modalities["output"] = [s.strip() for s in out_mod.split(",") if s.strip()]

        return self.key_edit.text().strip(), ModelConfig(
            name=self.name_edit.text().strip(),
            family=self.family_edit.text().strip(),
            release_date=self.release_date_edit.text().strip(),
            status=self.status_combo.currentText(),
            attachment=self.attachment_check.isChecked(),
            reasoning=self.reasoning_check.isChecked(),
            temperature=self.temperature_check.isChecked(),
            tool_call=self.tool_call_check.isChecked(),
            experimental=self.experimental_check.isChecked(),
            modalities=modalities if modalities else None,
            cost=cost,
            cost_context_over_200k=cost_over_200k,
            limit=limit,
            headers=headers,
            provider_override=provider_override,
            options=options,
            variants=variants,
        )
