from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class ProviderOptionType(str, Enum):
    API_KEY = "apiKey"
    BASE_URL = "baseURL"
    ENTERPRISE_URL = "enterpriseUrl"
    TIMEOUT = "timeout"
    HEADER_TIMEOUT = "headerTimeout"
    CHUNK_TIMEOUT = "chunkTimeout"


@dataclass
class ProviderOptions:
    api_key: str = ""
    base_url: str = ""
    enterprise_url: str = ""
    timeout: int | None = None
    header_timeout: int | None = None
    chunk_timeout: int | None = None
    set_cache_key: bool = False

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.api_key:
            d["apiKey"] = self.api_key
        if self.base_url:
            d["baseURL"] = self.base_url
        if self.enterprise_url:
            d["enterpriseUrl"] = self.enterprise_url
        if self.timeout is not None:
            d["timeout"] = self.timeout
        if self.header_timeout is not None:
            d["headerTimeout"] = self.header_timeout
        if self.chunk_timeout is not None:
            d["chunkTimeout"] = self.chunk_timeout
        if self.set_cache_key:
            d["setCacheKey"] = True
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProviderOptions:
        return cls(
            api_key=data.get("apiKey", ""),
            base_url=data.get("baseURL", ""),
            enterprise_url=data.get("enterpriseUrl", ""),
            timeout=data.get("timeout"),
            header_timeout=data.get("headerTimeout"),
            chunk_timeout=data.get("chunkTimeout"),
            set_cache_key=data.get("setCacheKey", False),
        )


@dataclass
class ModelCost:
    input: float = 0.0
    output: float = 0.0
    cache_read: float | None = None
    cache_write: float | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"input": self.input, "output": self.output}
        if self.cache_read is not None:
            d["cache_read"] = self.cache_read
        if self.cache_write is not None:
            d["cache_write"] = self.cache_write
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelCost:
        return cls(
            input=data.get("input", 0.0),
            output=data.get("output", 0.0),
            cache_read=data.get("cache_read"),
            cache_write=data.get("cache_write"),
        )


@dataclass
class ModelLimit:
    context: int = 0
    input: int | None = None
    output: int = 0

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"context": self.context, "output": self.output}
        if self.input is not None:
            d["input"] = self.input
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelLimit:
        return cls(
            context=data.get("context", 0),
            input=data.get("input"),
            output=data.get("output", 0),
        )


@dataclass
class ModelConfig:
    id: str = ""
    name: str = ""
    family: str = ""
    release_date: str = ""
    attachment: bool = False
    reasoning: bool = False
    temperature: bool = False
    tool_call: bool = False
    experimental: bool = False
    cost: ModelCost | None = None
    cost_context_over_200k: dict[str, Any] | None = None
    limit: ModelLimit | None = None
    modalities: dict[str, list[str]] | None = None
    status: str = "active"
    options: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    provider_override: dict[str, Any] = field(default_factory=dict)
    variants: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.id:
            d["id"] = self.id
        if self.name:
            d["name"] = self.name
        if self.family:
            d["family"] = self.family
        if self.release_date:
            d["release_date"] = self.release_date
        if self.attachment:
            d["attachment"] = True
        if self.reasoning:
            d["reasoning"] = True
        if self.temperature:
            d["temperature"] = True
        if self.tool_call:
            d["tool_call"] = True
        if self.experimental:
            d["experimental"] = True
        if self.cost:
            d["cost"] = self.cost.to_dict()
        if self.cost_context_over_200k:
            d["cost_over_200k"] = self.cost_context_over_200k
        if self.limit:
            d["limit"] = self.limit.to_dict()
        if self.modalities:
            d["modalities"] = self.modalities
        if self.status and self.status != "active":
            d["status"] = self.status
        if self.options:
            d["options"] = self.options
        if self.headers:
            d["headers"] = self.headers
        if self.provider_override:
            d["provider"] = self.provider_override
        if self.variants:
            d["variants"] = self.variants
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelConfig:
        cost_data = data.get("cost")
        limit_data = data.get("limit")
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            family=data.get("family", ""),
            release_date=data.get("release_date", ""),
            attachment=data.get("attachment", False),
            reasoning=data.get("reasoning", False),
            temperature=data.get("temperature", False),
            tool_call=data.get("tool_call", False),
            experimental=data.get("experimental", False),
            cost=ModelCost.from_dict(cost_data) if cost_data else None,
            cost_context_over_200k=data.get("cost_over_200k"),
            limit=ModelLimit.from_dict(limit_data) if limit_data else None,
            modalities=data.get("modalities"),
            status=data.get("status", "active"),
            options=data.get("options", {}),
            headers=data.get("headers", {}),
            provider_override=data.get("provider", {}),
            variants=data.get("variants", {}),
        )


@dataclass
class ProviderConfig:
    key: str = ""
    name: str = ""
    npm: str = "@ai-sdk/openai-compatible"
    api: str = ""
    options: ProviderOptions = field(default_factory=ProviderOptions)
    models: dict[str, ModelConfig] = field(default_factory=dict)
    env: list[str] = field(default_factory=list)
    whitelist: list[str] = field(default_factory=list)
    blacklist: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.npm:
            d["npm"] = self.npm
        if self.api:
            d["api"] = self.api
        opts = self.options.to_dict()
        if opts:
            d["options"] = opts
        if self.models:
            d["models"] = {k: v.to_dict() for k, v in self.models.items()}
        if self.env:
            d["env"] = self.env
        if self.whitelist:
            d["whitelist"] = self.whitelist
        if self.blacklist:
            d["blacklist"] = self.blacklist
        return d

    @classmethod
    def from_dict(cls, key: str, data: dict[str, Any]) -> ProviderConfig:
        models_data = data.get("models", {})
        return cls(
            key=key,
            name=data.get("name", ""),
            npm=data.get("npm", "@ai-sdk/openai-compatible"),
            api=data.get("api", ""),
            options=ProviderOptions.from_dict(data.get("options", {})),
            models={
                mk: ModelConfig.from_dict(mv)
                for mk, mv in models_data.items()
            },
            env=data.get("env", []),
            whitelist=data.get("whitelist", []),
            blacklist=data.get("blacklist", []),
        )


@dataclass
class AgentConfig:
    name: str = ""
    model: str = ""
    mode: str = "subagent"
    description: str = ""
    prompt: str = ""
    disable: bool = False
    hidden: bool = False
    color: str = ""
    steps: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    permission: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.model:
            d["model"] = self.model
        if self.mode and self.mode != "subagent":
            d["mode"] = self.mode
        if self.description:
            d["description"] = self.description
        if self.prompt:
            d["prompt"] = self.prompt
        if self.disable:
            d["disable"] = True
        if self.hidden:
            d["hidden"] = True
        if self.color:
            d["color"] = self.color
        if self.steps is not None:
            d["steps"] = self.steps
        if self.temperature is not None:
            d["temperature"] = self.temperature
        if self.top_p is not None:
            d["top_p"] = self.top_p
        if self.permission:
            d["permission"] = self.permission
        return d

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> AgentConfig:
        return cls(
            name=name,
            model=data.get("model", ""),
            mode=data.get("mode", "subagent"),
            description=data.get("description", ""),
            prompt=data.get("prompt", ""),
            disable=data.get("disable", False),
            hidden=data.get("hidden", False),
            color=data.get("color", ""),
            steps=data.get("steps"),
            temperature=data.get("temperature"),
            top_p=data.get("top_p"),
            permission=data.get("permission", {}),
        )


@dataclass
class McpServerConfig:
    name: str = ""
    server_type: str = "local"
    command: list[str] = field(default_factory=list)
    url: str = ""
    enabled: bool = True
    env: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    cwd: str = ""
    timeout: int | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"type": self.server_type}
        if self.server_type == "local":
            d["command"] = self.command
            if self.cwd:
                d["cwd"] = self.cwd
            if self.env:
                d["environment"] = self.env
        else:
            d["url"] = self.url
            if self.headers:
                d["headers"] = self.headers
        if not self.enabled:
            d["enabled"] = False
        if self.timeout is not None:
            d["timeout"] = self.timeout
        return d

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> McpServerConfig:
        return cls(
            name=name,
            server_type=data.get("type", "local"),
            command=data.get("command", []),
            url=data.get("url", ""),
            enabled=data.get("enabled", True),
            env=data.get("environment", data.get("env", {})),
            headers=data.get("headers", {}),
            cwd=data.get("cwd", ""),
            timeout=data.get("timeout"),
        )


@dataclass
class OpenCodeConfig:
    schema_url: str = "https://opencode.ai/config.json"
    username: str = ""
    model: str = ""
    small_model: str = ""
    default_agent: str = ""
    shell: str = ""
    log_level: str = "INFO"
    share: str = "manual"
    autoupdate: bool | str = True
    snapshot: bool = True
    instructions: list[str] = field(default_factory=list)
    disabled_providers: list[str] = field(default_factory=list)
    enabled_providers: list[str] = field(default_factory=list)
    providers: dict[str, ProviderConfig] = field(default_factory=dict)
    agents: dict[str, AgentConfig] = field(default_factory=dict)
    mcp_servers: dict[str, McpServerConfig] = field(default_factory=dict)
    permission: dict[str, Any] = field(default_factory=dict)
    experimental: dict[str, Any] = field(default_factory=dict)
    server: dict[str, Any] = field(default_factory=dict)
    command: dict[str, Any] = field(default_factory=dict)
    skills: dict[str, Any] = field(default_factory=dict)
    references: dict[str, Any] = field(default_factory=dict)
    watcher: dict[str, Any] = field(default_factory=dict)
    plugin: list[Any] = field(default_factory=list)
    formatter: Any = None
    lsp: Any = None
    tools: dict[str, bool] = field(default_factory=dict)
    attachment: dict[str, Any] = field(default_factory=dict)
    enterprise: dict[str, Any] = field(default_factory=dict)
    tool_output: dict[str, Any] = field(default_factory=dict)
    compaction: dict[str, Any] = field(default_factory=dict)
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"$schema": self.schema_url}
        if self.username:
            d["username"] = self.username
        if self.model:
            d["model"] = self.model
        if self.small_model:
            d["small_model"] = self.small_model
        if self.default_agent:
            d["default_agent"] = self.default_agent
        if self.shell:
            d["shell"] = self.shell
        if self.log_level and self.log_level != "INFO":
            d["logLevel"] = self.log_level
        if self.share and self.share != "manual":
            d["share"] = self.share
        if self.autoupdate is not True:
            d["autoupdate"] = self.autoupdate
        if self.snapshot is not True:
            d["snapshot"] = self.snapshot
        if self.instructions:
            d["instructions"] = self.instructions
        if self.disabled_providers:
            d["disabled_providers"] = self.disabled_providers
        if self.enabled_providers:
            d["enabled_providers"] = self.enabled_providers
        if self.providers:
            d["provider"] = {k: v.to_dict() for k, v in self.providers.items()}
        if self.agents:
            d["agent"] = {k: v.to_dict() for k, v in self.agents.items()}
        if self.mcp_servers:
            d["mcp"] = {k: v.to_dict() for k, v in self.mcp_servers.items()}
        if self.permission:
            d["permission"] = self.permission
        if self.experimental:
            d["experimental"] = self.experimental
        if self.server:
            d["server"] = self.server
        if self.command:
            d["command"] = self.command
        if self.skills:
            d["skills"] = self.skills
        if self.references:
            d["references"] = self.references
        if self.watcher:
            d["watcher"] = self.watcher
        if self.plugin:
            d["plugin"] = self.plugin
        if self.formatter is not None:
            d["formatter"] = self.formatter
        if self.lsp is not None:
            d["lsp"] = self.lsp
        if self.tools:
            d["tools"] = self.tools
        if self.attachment:
            d["attachment"] = self.attachment
        if self.enterprise:
            d["enterprise"] = self.enterprise
        if self.tool_output:
            d["tool_output"] = self.tool_output
        if self.compaction:
            d["compaction"] = self.compaction
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OpenCodeConfig:
        providers_data = data.get("provider", {})
        agents_data = data.get("agent", {})
        mcp_data = data.get("mcp", {})
        return cls(
            schema_url=data.get("$schema", "https://opencode.ai/config.json"),
            username=data.get("username", ""),
            model=data.get("model", ""),
            small_model=data.get("small_model", ""),
            default_agent=data.get("default_agent", ""),
            shell=data.get("shell", ""),
            log_level=data.get("logLevel", "INFO"),
            share=data.get("share", "manual"),
            autoupdate=data.get("autoupdate", True),
            snapshot=data.get("snapshot", True),
            instructions=data.get("instructions", []),
            disabled_providers=data.get("disabled_providers", []),
            enabled_providers=data.get("enabled_providers", []),
            providers={
                k: ProviderConfig.from_dict(k, v)
                for k, v in providers_data.items()
            },
            agents={
                k: AgentConfig.from_dict(k, v)
                for k, v in agents_data.items()
            },
            mcp_servers={
                k: McpServerConfig.from_dict(k, v)
                for k, v in mcp_data.items()
            },
            permission=data.get("permission", {}),
            experimental=data.get("experimental", {}),
            server=data.get("server", {}),
            command=data.get("command", {}),
            skills=data.get("skills", {}),
            references=data.get("references", {}),
            watcher=data.get("watcher", {}),
            plugin=data.get("plugin", []),
            formatter=data.get("formatter"),
            lsp=data.get("lsp"),
            tools=data.get("tools", {}),
            attachment=data.get("attachment", {}),
            enterprise=data.get("enterprise", {}),
            tool_output=data.get("tool_output", {}),
            compaction=data.get("compaction", {}),
            raw_data=data,
        )
