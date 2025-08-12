from __future__ import annotations

from typing import List, Optional

import httpx

from ..config import KForgeConfig
from ..types import ComputeOffer, Instance
from .base import Provider


class LambdaLabsProvider(Provider):
    def __init__(self, config: KForgeConfig) -> None:
        self._config = config
        self._client = httpx.Client(base_url="https://cloud.lambdalabs.com/api")

    @property
    def name(self) -> str:
        return "lambdalabs"

    def list_instances(self) -> List[Instance]:
        # TODO: Implement Lambda Labs API call
        return []

    def get_available_compute(self) -> List[ComputeOffer]:
        # TODO: Implement call to list available GPU types and prices
        return []

    def run_experiment(
        self,
        *,
        branch: str,
        repo_url: Optional[str],
        repo_commit: Optional[str],
        selected_gpu: str,
    ) -> str:
        # TODO: Implement Lambda Labs job submission using selected_gpu
        return "lambdalabs:pending"

    def stop_instance(self, instance_id: str) -> None:
        # TODO: Implement stop call
        return None
