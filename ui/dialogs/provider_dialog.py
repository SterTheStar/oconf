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

from core.models import AgentConfig, ProviderConfig, ProviderOptions


class ProviderDialog(QDialog):
    def __init__(self, provider: ProviderConfig | None = None, parent=None):
        super().__init__(parent)
        self._provider = provider
        self._is_edit = provider is not None
        self.setWindowTitle("Edit Provider" if self._is_edit else "Add Provider")
        self.setMinimumSize(580, 500)
        self.resize(620, 550)
        self._build_ui()
        if self._is_edit and provider:
            self._load_data(provider)

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
        self.key_edit.setPlaceholderText("e.g. anthropic, openai, my-provider")
        basic_form.addRow("Key:", self.key_edit)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Display name")
        basic_form.addRow("Name:", self.name_edit)

        self.npm_edit = QLineEdit()
        self.npm_edit.setPlaceholderText("@ai-sdk/openai-compatible")
        basic_form.addRow("NPM Package:", self.npm_edit)

        self.api_edit = QLineEdit()
        self.api_edit.setPlaceholderText("API identifier (optional)")
        basic_form.addRow("API:", self.api_edit)

        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("https://api.example.com/v1")
        basic_form.addRow("Base URL:", self.base_url_edit)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("API key (stored in config)")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        basic_form.addRow("API Key:", self.api_key_edit)

        self.enterprise_url_edit = QLineEdit()
        self.enterprise_url_edit.setPlaceholderText("GitHub Enterprise URL (optional)")
        basic_form.addRow("Enterprise URL:", self.enterprise_url_edit)

        self.env_edit = QLineEdit()
        self.env_edit.setPlaceholderText("Comma-separated (e.g. ANTHROPIC_API_KEY)")
        basic_form.addRow("Env Vars:", self.env_edit)

        tab_basic_layout.addLayout(basic_form)
        tab_basic_layout.addStretch()
        tabs.addTab(tab_basic, "Basic")

        tab_advanced = QWidget()
        tab_advanced_layout = QVBoxLayout(tab_advanced)
        tab_advanced_layout.setContentsMargins(12, 12, 12, 12)

        adv_form = QFormLayout()
        adv_form.setSpacing(8)

        self.set_cache_key_check = QCheckBox("Enable prompt cache key")
        adv_form.addRow("Cache Key:", self.set_cache_key_check)

        timeout_layout = QHBoxLayout()
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(0, 300000)
        self.timeout_spin.setSpecialValueText("Default")
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addWidget(QLabel("ms"))
        adv_form.addRow("Timeout:", timeout_layout)

        header_timeout_layout = QHBoxLayout()
        self.header_timeout_spin = QSpinBox()
        self.header_timeout_spin.setRange(0, 300000)
        self.header_timeout_spin.setSpecialValueText("Default")
        header_timeout_layout.addWidget(self.header_timeout_spin)
        header_timeout_layout.addWidget(QLabel("ms"))
        adv_form.addRow("Header Timeout:", header_timeout_layout)

        chunk_timeout_layout = QHBoxLayout()
        self.chunk_timeout_spin = QSpinBox()
        self.chunk_timeout_spin.setRange(0, 300000)
        self.chunk_timeout_spin.setSpecialValueText("Default")
        chunk_timeout_layout.addWidget(self.chunk_timeout_spin)
        chunk_timeout_layout.addWidget(QLabel("ms"))
        adv_form.addRow("Chunk Timeout:", chunk_timeout_layout)

        tab_advanced_layout.addLayout(adv_form)

        filter_group = QGroupBox("Model Filtering")
        filter_form = QFormLayout(filter_group)
        filter_form.setSpacing(8)

        self.whitelist_edit = QLineEdit()
        self.whitelist_edit.setPlaceholderText("Comma-separated. If set, only these models are available")
        filter_form.addRow("Whitelist:", self.whitelist_edit)

        self.blacklist_edit = QLineEdit()
        self.blacklist_edit.setPlaceholderText("Comma-separated. These models will be hidden")
        filter_form.addRow("Blacklist:", self.blacklist_edit)

        tab_advanced_layout.addWidget(filter_group)
        tab_advanced_layout.addStretch()
        tabs.addTab(tab_advanced, "Advanced")

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

    def _load_data(self, p: ProviderConfig):
        self.key_edit.setText(p.key)
        self.name_edit.setText(p.name)
        self.npm_edit.setText(p.npm)
        self.api_edit.setText(p.api)
        self.base_url_edit.setText(p.options.base_url)
        self.api_key_edit.setText(p.options.api_key)
        self.enterprise_url_edit.setText(p.options.enterprise_url)
        if p.options.timeout is not None:
            self.timeout_spin.setValue(p.options.timeout)
        if p.options.header_timeout is not None:
            self.header_timeout_spin.setValue(p.options.header_timeout)
        if p.options.chunk_timeout is not None:
            self.chunk_timeout_spin.setValue(p.options.chunk_timeout)
        self.env_edit.setText(", ".join(p.env))
        self.whitelist_edit.setText(", ".join(p.whitelist))
        self.blacklist_edit.setText(", ".join(p.blacklist))

    def get_provider(self) -> ProviderConfig:
        env_text = self.env_edit.text().strip()
        env = [e.strip() for e in env_text.split(",") if e.strip()] if env_text else []
        whitelist_text = self.whitelist_edit.text().strip()
        whitelist = [e.strip() for e in whitelist_text.split(",") if e.strip()] if whitelist_text else []
        blacklist_text = self.blacklist_edit.text().strip()
        blacklist = [e.strip() for e in blacklist_text.split(",") if e.strip()] if blacklist_text else []
        timeout = self.timeout_spin.value() if self.timeout_spin.value() > 0 else None
        header_timeout = self.header_timeout_spin.value() if self.header_timeout_spin.value() > 0 else None
        chunk_timeout = self.chunk_timeout_spin.value() if self.chunk_timeout_spin.value() > 0 else None
        return ProviderConfig(
            key=self.key_edit.text().strip(),
            name=self.name_edit.text().strip(),
            npm=self.npm_edit.text().strip() or "@ai-sdk/openai-compatible",
            api=self.api_edit.text().strip(),
            options=ProviderOptions(
                base_url=self.base_url_edit.text().strip(),
                api_key=self.api_key_edit.text().strip(),
                enterprise_url=self.enterprise_url_edit.text().strip(),
                timeout=timeout,
                header_timeout=header_timeout,
                chunk_timeout=chunk_timeout,
                set_cache_key=self.set_cache_key_check.isChecked(),
            ),
            env=env,
            whitelist=whitelist,
            blacklist=blacklist,
        )


class AgentDialog(QDialog):
    def __init__(self, agent_name: str = "", agent: AgentConfig | None = None, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._is_edit = agent is not None
        self.setWindowTitle("Edit Agent" if self._is_edit else "Add Agent")
        self.setMinimumSize(600, 480)
        self.resize(640, 520)
        self._build_ui()
        if self._is_edit and agent:
            self._load_data(agent_name, agent)

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
        self.name_edit.setPlaceholderText("e.g. my-reviewer")
        basic_form.addRow("Name:", self.name_edit)

        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("provider/model-id (e.g. anthropic/claude-sonnet-4-6)")
        basic_form.addRow("Model:", self.model_edit)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["subagent", "primary", "all"])
        basic_form.addRow("Mode:", self.mode_combo)

        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("When to use this agent")
        basic_form.addRow("Description:", self.description_edit)

        self.color_edit = QLineEdit()
        self.color_edit.setPlaceholderText("#FF5733 or primary, secondary, accent, etc.")
        basic_form.addRow("Color:", self.color_edit)

        tab_basic_layout.addLayout(basic_form)
        tab_basic_layout.addStretch()
        tabs.addTab(tab_basic, "Basic")

        tab_behavior = QWidget()
        tab_behavior_layout = QVBoxLayout(tab_behavior)
        tab_behavior_layout.setContentsMargins(12, 12, 12, 12)

        behavior_form = QFormLayout()
        behavior_form.setSpacing(8)

        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(0, 1000)
        self.steps_spin.setSpecialValueText("Default")
        behavior_form.addRow("Max Steps:", self.steps_spin)

        temp_layout = QHBoxLayout()
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setDecimals(2)
        self.temperature_spin.setSpecialValueText("Default")
        temp_layout.addWidget(self.temperature_spin)
        behavior_form.addRow("Temperature:", temp_layout)

        top_p_layout = QHBoxLayout()
        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0)
        self.top_p_spin.setSingleStep(0.05)
        self.top_p_spin.setDecimals(2)
        self.top_p_spin.setSpecialValueText("Default")
        top_p_layout.addWidget(self.top_p_spin)
        behavior_form.addRow("Top P:", top_p_layout)

        self.disable_check = QCheckBox("Disable this agent")
        behavior_form.addRow("Status:", self.disable_check)

        self.hidden_check = QCheckBox("Hide from autocomplete")
        behavior_form.addRow("Visibility:", self.hidden_check)

        tab_behavior_layout.addLayout(behavior_form)

        perm_group = QGroupBox("Permissions (JSON)")
        perm_layout = QVBoxLayout(perm_group)
        self.permission_edit = QTextEdit()
        self.permission_edit.setPlaceholderText('{"edit": "deny", "bash": {"git *": "allow"}}')
        self.permission_edit.setMaximumHeight(80)
        perm_layout.addWidget(self.permission_edit)
        tab_behavior_layout.addWidget(perm_group)

        tab_behavior_layout.addStretch()
        tabs.addTab(tab_behavior, "Behavior")

        tab_prompt = QWidget()
        tab_prompt_layout = QVBoxLayout(tab_prompt)
        tab_prompt_layout.setContentsMargins(12, 12, 12, 12)

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("System prompt for this agent...")
        tab_prompt_layout.addWidget(self.prompt_edit)

        tabs.addTab(tab_prompt, "Prompt")

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

    def _load_data(self, name: str, a: AgentConfig):
        self.name_edit.setText(name)
        self.model_edit.setText(a.model)
        idx = self.mode_combo.findText(a.mode)
        if idx >= 0:
            self.mode_combo.setCurrentIndex(idx)
        self.description_edit.setText(a.description)
        self.color_edit.setText(a.color)
        if a.steps is not None:
            self.steps_spin.setValue(a.steps)
        if a.temperature is not None:
            self.temperature_spin.setValue(a.temperature)
        if a.top_p is not None:
            self.top_p_spin.setValue(a.top_p)
        self.disable_check.setChecked(a.disable)
        self.hidden_check.setChecked(a.hidden)
        if a.permission:
            self.permission_edit.setPlainText(json.dumps(a.permission, indent=2))
        self.prompt_edit.setPlainText(a.prompt)

    def get_agent(self) -> tuple[str, AgentConfig]:
        steps = self.steps_spin.value() if self.steps_spin.value() > 0 else None
        temp = self.temperature_spin.value() if self.temperature_spin.value() > 0 else None
        top_p = self.top_p_spin.value() if self.top_p_spin.value() > 0 else None

        permission = {}
        perm_text = self.permission_edit.toPlainText().strip()
        if perm_text:
            try:
                permission = json.loads(perm_text)
            except json.JSONDecodeError:
                permission = {}

        return self.name_edit.text().strip(), AgentConfig(
            name=self.name_edit.text().strip(),
            model=self.model_edit.text().strip(),
            mode=self.mode_combo.currentText(),
            description=self.description_edit.text().strip(),
            prompt=self.prompt_edit.toPlainText().strip(),
            disable=self.disable_check.isChecked(),
            hidden=self.hidden_check.isChecked(),
            color=self.color_edit.text().strip(),
            steps=steps,
            temperature=temp,
            top_p=top_p,
            permission=permission,
        )
