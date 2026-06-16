from __future__ import annotations

import json
import urllib.request
import urllib.error
from dataclasses import dataclass

from core.models import ModelConfig, ProviderConfig


@dataclass
class FetchResult:
    total: int = 0
    added: int = 0
    skipped: int = 0
    errors: list[str] | None = None


def fetch_models(provider: ProviderConfig) -> tuple[list[str], str | None]:
    """Fetch model IDs from provider's /v1/models endpoint.

    Returns (model_ids, error_message).
    """
    base_url = provider.options.base_url.rstrip("/")
    if not base_url:
        return [], "No base URL configured for this provider."

    url = f"{base_url}/models"

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if provider.options.api_key:
        headers["Authorization"] = f"Bearer {provider.options.api_key}"

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
    except urllib.error.HTTPError as e:
        return [], f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return [], f"Connection error: {e.reason}"
    except json.JSONDecodeError:
        return [], "Invalid JSON response"
    except Exception as e:
        return [], str(e)

    models_list = data.get("data", [])
    if not isinstance(models_list, list):
        return [], "Unexpected response format (expected 'data' array)"

    ids: list[str] = []
    for item in models_list:
        mid = item.get("id", "")
        if mid:
            ids.append(mid)

    return ids, None


def add_models_from_api(
    provider: ProviderConfig,
    existing_keys: set[str],
) -> FetchResult:
    """Fetch models from API and add missing ones to the provider.

    Returns a FetchResult with counts.
    """
    ids, error = fetch_models(provider)
    if error:
        return FetchResult(errors=[error])

    result = FetchResult(total=len(ids))
    for mid in ids:
        if mid in existing_keys:
            result.skipped += 1
            continue
        provider.models[mid] = ModelConfig(name=mid)
        result.added += 1

    return result
