from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator


class Service(BaseModel):
    name: str
    url: str
    timeout_s: float = Field(default=5.0, gt=0, le=60)
    expect_status: int = 200

    @field_validator("url")
    @classmethod
    def must_be_http(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        return v


class Config(BaseModel):
    services: list[Service]
    backup_bucket: str | None = None


def load_config(path: Path) -> Config:
    """Read YAML safely (never yaml.load) and validate it."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Config.model_validate(data)


def token_from_env(name: str = "SHOP_TOKEN") -> str:
    token = os.environ.get(name)
    if not token:
        raise RuntimeError(f"{name} is not set")
    return token
