from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path


class BackupManager:
    """Manages automatic backups of the config file."""

    def __init__(self, config_path: str | Path, backup_dir: str | Path | None = None):
        self.config_path = Path(config_path)
        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            self.backup_dir = self.config_path.parent / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> Path | None:
        if not self.config_path.exists():
            return None
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"opencode_{ts}.jsonc"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(self.config_path, backup_path)
        self._prune_old_backups(max_backups=20)
        return backup_path

    def list_backups(self) -> list[Path]:
        backups = sorted(
            self.backup_dir.glob("opencode_*.jsonc"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return backups

    def restore_backup(self, backup_path: Path) -> bool:
        if not backup_path.exists():
            return False
        self.create_backup()
        shutil.copy2(backup_path, self.config_path)
        return True

    def _prune_old_backups(self, max_backups: int = 20) -> None:
        backups = self.list_backups()
        for old in backups[max_backups:]:
            old.unlink(missing_ok=True)
