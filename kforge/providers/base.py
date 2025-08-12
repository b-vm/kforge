from __future__ import annotations

import abc
from typing import List, Optional

from ..types import ComputeOffer, Instance


class Provider(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:  # e.g. "runpod", "lambdalabs"
        raise NotImplementedError

    @abc.abstractmethod
    def list_instances(self) -> List[Instance]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_available_compute(self) -> List[ComputeOffer]:
        """Return available GPU offerings with pricing info."""
        raise NotImplementedError

    @abc.abstractmethod
    def run_experiment(
        self,
        *,
        branch: str,
        repo_url: Optional[str],
        repo_commit: Optional[str],
        selected_gpu: str,
    ) -> str:
        """Submit an experiment and return a provider-scoped experiment ID."""
        raise NotImplementedError

    @abc.abstractmethod
    def stop_instance(self, instance_id: str) -> None:
        raise NotImplementedError
