from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.backup_manager import BackupManager
from core.models import OpenCodeConfig


class ConfigManager:
    """Reads, validates, and writes the opencode.jsonc file."""

    def __init__(self, config_path: str | Path | None = None):
        if config_path is None:
            config_path = Path.home() / ".config" / "opencode" / "opencode.jsonc"
        self.config_path = Path(config_path)
        self.backup_manager = BackupManager(self.config_path)
        self._config: OpenCodeConfig = OpenCodeConfig()

    @property
    def config(self) -> OpenCodeConfig:
        return self._config

    def load(self) -> OpenCodeConfig:
        if not self.config_path.exists():
            self._config = OpenCodeConfig()
            return self._config
        raw_text = self.config_path.read_text(encoding="utf-8")
        parsed = self._parse_jsonc(raw_text)
        self._config = OpenCodeConfig.from_dict(parsed)
        return self._config

    def save(self) -> bool:
        self.backup_manager.create_backup()
        data = self._config.to_dict()
        text = json.dumps(data, indent=2, ensure_ascii=False)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(text, encoding="utf-8")
        return True

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.config_path.exists():
            return errors
        raw = self.config_path.read_text(encoding="utf-8")
        try:
            self._parse_jsonc(raw)
        except json.JSONDecodeError as e:
            errors.append(f"JSON parse error: {e}")
        if self._config.model and "/" not in self._config.model:
            errors.append(f"Model should be in format provider/model-id: {self._config.model}")
        if self._config.small_model and "/" not in self._config.small_model:
            errors.append(f"Small model should be in format provider/model-id: {self._config.small_model}")
        for name, agent in self._config.agents.items():
            if agent.mode not in ("subagent", "primary", "all", ""):
                errors.append(f"Agent '{name}' has invalid mode: {agent.mode}")
        for name, mcp in self._config.mcp_servers.items():
            if mcp.server_type == "local" and not mcp.command:
                errors.append(f"MCP server '{name}' is local but has no command")
            if mcp.server_type == "remote" and not mcp.url:
                errors.append(f"MCP server '{name}' is remote but has no URL")
        return errors

    def create_default(self) -> None:
        self._config = OpenCodeConfig()
        self.save()

    def apply_raw_json(self, text: str) -> list[str]:
        try:
            parsed = self._parse_jsonc(text)
        except json.JSONDecodeError as e:
            return [f"JSON parse error: {e}"]
        self._config = OpenCodeConfig.from_dict(parsed)
        return []

    def _parse_jsonc(self, text: str) -> dict[str, Any]:
        text = self._strip_comments(text)
        text = self._strip_trailing_commas(text)
        return json.loads(text)

    def _strip_comments(self, text: str) -> str:
        result: list[str] = []
        i = 0
        in_string = False
        escape = False
        while i < len(text):
            ch = text[i]
            if escape:
                result.append(ch)
                escape = False
                i += 1
                continue
            if in_string:
                if ch == "\\":
                    escape = True
                    result.append(ch)
                    i += 1
                    continue
                if ch == '"':
                    in_string = False
                result.append(ch)
                i += 1
                continue
            if ch == '"':
                in_string = True
                result.append(ch)
                i += 1
                continue
            if ch == "/":
                if i + 1 < len(text) and text[i + 1] == "/":
                    while i < len(text) and text[i] != "\n":
                        i += 1
                    continue
                if i + 1 < len(text) and text[i + 1] == "*":
                    i += 2
                    while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                        i += 1
                    i += 2
                    continue
            result.append(ch)
            i += 1
        return "".join(result)

    def _strip_trailing_commas(self, text: str) -> str:
        return re.sub(r",\s*([}\]])", r"\1", text)
