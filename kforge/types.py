from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Instance:
    id: str
    name: Optional[str]
    provider: str
    status: str
    gpu_type: Optional[str]


@dataclass
class RunRequest:
    branch: str
    repo_path: Path


@dataclass
class ComputeOffer:
    provider: str
    gpu_type: str
    price_per_hour: float
    description: Optional[str] = None
