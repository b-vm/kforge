from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_DIR_NAME = ".kforge"
CONFIG_FILE_NAME = "config.toml"


@dataclass
class RunpodConfig:
    api_key: Optional[str] = None


@dataclass
class LambdaLabsConfig:
    api_key: Optional[str] = None


@dataclass
class S3Config:
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    bucket: Optional[str] = None
    region: Optional[str] = None


@dataclass
class PreferencesConfig:
    gpu_priority: list[str] = field(default_factory=list)


@dataclass
class KForgeConfig:
    s3: S3Config = field(default_factory=S3Config)
    runpod: RunpodConfig = field(default_factory=RunpodConfig)
    lambdalabs: LambdaLabsConfig = field(default_factory=LambdaLabsConfig)
    preferences: PreferencesConfig = field(default_factory=PreferencesConfig)


def get_config_dir() -> Path:
    return Path(os.path.expanduser("~")) / CONFIG_DIR_NAME


def get_config_path() -> Path:
    return get_config_dir() / CONFIG_FILE_NAME


def ensure_config_initialized() -> None:
    cfg_dir = get_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = get_config_path()
    if not cfg_path.exists():
        # Minimal TOML skeleton
        content = """
# KForge configuration

[s3]
# access_key_id = ""
# secret_access_key = ""
# bucket = ""
# region = ""

[runpod]
# api_key = ""

[lambdalabs]
# api_key = ""

[preferences]
# Ordered by preference; first match wins
# Known examples: "rtx5090", "rtx5000-ada", "a100-40gb"
gpu_priority = ["rtx5090", "rtx5000-ada", "a100-40gb"]
""".lstrip()
        cfg_path.write_text(content, encoding="utf-8")


def _read_toml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as fp:
        return tomllib.load(fp)


def load_config() -> KForgeConfig:
    data = _read_toml(get_config_path())

    s3_tbl = data.get("s3", {})
    runpod_tbl = data.get("runpod", {})
    lambda_tbl = data.get("lambdalabs", {})
    prefs_tbl = data.get("preferences", {})

    return KForgeConfig(
        s3=S3Config(
            access_key_id=s3_tbl.get("access_key_id"),
            secret_access_key=s3_tbl.get("secret_access_key"),
            bucket=s3_tbl.get("bucket"),
            region=s3_tbl.get("region"),
        ),
        runpod=RunpodConfig(api_key=runpod_tbl.get("api_key")),
        lambdalabs=LambdaLabsConfig(api_key=lambda_tbl.get("api_key")),
        preferences=PreferencesConfig(
            gpu_priority=list(prefs_tbl.get("gpu_priority", []))
        ),
    )
