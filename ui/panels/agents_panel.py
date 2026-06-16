from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import ConfigManager
from core.models import AgentConfig
from ui.styles import VSCodeColors


class AgentDetailPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        self.title_label = QLabel("Select an agent")
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.info_label = QLabel("")
        self.info_label.setObjectName("subtitleLabel")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.prompt_label = QTextEdit()
        self.prompt_label.setReadOnly(True)
        self.prompt_label.setPlaceholderText("Agent prompt will appear here...")
        layout.addWidget(self.prompt_label, 1)

    def show_agent(self, name: str, agent: AgentConfig):
        self.title_label.setText(name)
        lines = []
        if agent.model:
            lines.append(f"Model: {agent.model}")
        if agent.mode:
            lines.append(f"Mode: {agent.mode}")
        if agent.description:
            lines.append(f"Description: {agent.description}")
        if agent.color:
            lines.append(f"Color: {agent.color}")
        if agent.steps is not None:
            lines.append(f"Steps: {agent.steps}")
        if agent.temperature is not None:
            lines.append(f"Temperature: {agent.temperature}")
        if agent.disable:
            lines.append("Status: DISABLED")
        if agent.hidden:
            lines.append("Hidden: yes")
        self.info_label.setText("\n".join(lines) if lines else "Default configuration")
        self.prompt_label.setPlainText(agent.prompt or "")

    def clear(self):
        self.title_label.setText("Select an agent")
        self.info_label.setText("")
        self.prompt_label.setPlainText("")


class AgentsPanel(QWidget):
    config_changed = Signal()

    BUILTIN_AGENTS = {"build", "plan", "general", "explore", "title", "summary", "compaction"}

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.cm = config_manager
        self._selected_agent: str | None = None
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
        title = QLabel("Agents")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ Add Agent")
        add_btn.setObjectName("primaryBtn")
        add_btn.setMinimumHeight(36)
        add_btn.clicked.connect(self._add_agent)
        header.addWidget(add_btn)
        left_layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Mode", "Status"])
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
        edit_btn.clicked.connect(self._edit_agent)
        btn_row.addWidget(edit_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.setMinimumHeight(34)
        delete_btn.clicked.connect(self._delete_agent)
        btn_row.addWidget(delete_btn)
        left_layout.addLayout(btn_row)

        content.addWidget(left, 1)

        self.detail = AgentDetailPanel()
        self.detail.setFixedWidth(380)
        content.addWidget(self.detail)

        outer.addLayout(content)

    def load_data(self):
        agents = self.cm.config.agents
        self.table.setRowCount(len(agents))
        for row, (name, agent) in enumerate(agents.items()):
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, name)
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, QTableWidgetItem(agent.mode))
            status = "Disabled" if agent.disable else "Active"
            self.table.setItem(row, 2, QTableWidgetItem(status))
        self.detail.clear()
        self._selected_agent = None

    def _on_select(self, row, col, prev_row, prev_col):
        if row < 0:
            return
        name_item = self.table.item(row, 0)
        if name_item:
            name = name_item.data(Qt.UserRole)
            self._selected_agent = name
            agent = self.cm.config.agents.get(name)
            if agent:
                self.detail.show_agent(name, agent)

    def _add_agent(self):
        from ui.dialogs.provider_dialog import AgentDialog
        dlg = AgentDialog(parent=self)
        if dlg.exec():
            name, agent = dlg.get_agent()
            if name in self.cm.config.agents:
                QMessageBox.warning(self, "Error", f"Agent '{name}' already exists.")
                return
            self.cm.config.agents[name] = agent
            self.cm.save()
            self.load_data()
            self.config_changed.emit()

    def _edit_agent(self):
        if not self._selected_agent:
            return
        agent = self.cm.config.agents.get(self._selected_agent)
        if not agent:
            return
        from ui.dialogs.provider_dialog import AgentDialog
        dlg = AgentDialog(agent_name=self._selected_agent, agent=agent, parent=self)
        if dlg.exec():
            new_name, updated = dlg.get_agent()
            if new_name != self._selected_agent:
                del self.cm.config.agents[self._selected_agent]
            self.cm.config.agents[new_name] = updated
            self.cm.save()
            self.load_data()
            self.config_changed.emit()

    def _delete_agent(self):
        if not self._selected_agent:
            return
        reply = QMessageBox.question(
            self, "Delete Agent",
            f"Delete agent '{self._selected_agent}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            del self.cm.config.agents[self._selected_agent]
            self.cm.save()
            self.load_data()
            self.config_changed.emit()
