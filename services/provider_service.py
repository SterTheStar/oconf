from __future__ import annotations

from core.config_manager import ConfigManager
from core.models import ProviderConfig


class ProviderService:
    """Service layer for provider CRUD operations."""

    def __init__(self, config_manager: ConfigManager):
        self.cm = config_manager

    def get_all(self) -> dict[str, ProviderConfig]:
        return self.cm.config.providers

    def get(self, key: str) -> ProviderConfig | None:
        return self.cm.config.providers.get(key)

    def add(self, provider: ProviderConfig) -> bool:
        if provider.key in self.cm.config.providers:
            return False
        self.cm.config.providers[provider.key] = provider
        return True

    def update(self, key: str, provider: ProviderConfig) -> bool:
        if key not in self.cm.config.providers:
            return False
        if key != provider.key:
            del self.cm.config.providers[key]
        self.cm.config.providers[provider.key] = provider
        return True

    def remove(self, key: str) -> bool:
        if key not in self.cm.config.providers:
            return False
        del self.cm.config.providers[key]
        if key in self.cm.config.disabled_providers:
            self.cm.config.disabled_providers.remove(key)
        return True

    def toggle_enabled(self, key: str) -> bool:
        if key in self.cm.config.disabled_providers:
            self.cm.config.disabled_providers.remove(key)
            return True
        elif key in self.cm.config.providers:
            self.cm.config.disabled_providers.append(key)
            return False
        return False

    def is_enabled(self, key: str) -> bool:
        if self.cm.config.enabled_providers:
            return key in self.cm.config.enabled_providers
        return key not in self.cm.config.disabled_providers
