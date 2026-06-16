from __future__ import annotations

from core.config_manager import ConfigManager
from core.models import ModelConfig, ProviderConfig


class ModelService:
    """Service layer for model CRUD operations within providers."""

    def __init__(self, config_manager: ConfigManager):
        self.cm = config_manager

    def get_models(self, provider_key: str) -> dict[str, ModelConfig]:
        provider = self.cm.config.providers.get(provider_key)
        if not provider:
            return {}
        return provider.models

    def get_model(self, provider_key: str, model_key: str) -> ModelConfig | None:
        provider = self.cm.config.providers.get(provider_key)
        if not provider:
            return None
        return provider.models.get(model_key)

    def add_model(self, provider_key: str, model_key: str, model: ModelConfig) -> bool:
        provider = self.cm.config.providers.get(provider_key)
        if not provider:
            return False
        if model_key in provider.models:
            return False
        provider.models[model_key] = model
        return True

    def update_model(self, provider_key: str, old_key: str, new_key: str, model: ModelConfig) -> bool:
        provider = self.cm.config.providers.get(provider_key)
        if not provider or old_key not in provider.models:
            return False
        if old_key != new_key:
            del provider.models[old_key]
        provider.models[new_key] = model
        return True

    def remove_model(self, provider_key: str, model_key: str) -> bool:
        provider = self.cm.config.providers.get(provider_key)
        if not provider or model_key not in provider.models:
            return False
        del provider.models[model_key]
        return True
