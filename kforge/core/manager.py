from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from ..config import KForgeConfig, ensure_config_initialized, load_config
from ..providers.base import Provider
from ..providers.lambdalabs import LambdaLabsProvider
from ..providers.runpod import RunpodProvider
from ..types import ComputeOffer, Instance


@dataclass
class _RepoInfo:
    url: Optional[str]
    commit: Optional[str]


def _detect_git_repo_info(repo_path: Path) -> _RepoInfo:
    def _git(args: list[str]) -> Optional[str]:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=str(repo_path),
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() or None
        except Exception:
            return None

    origin_url = _git(["config", "--get", "remote.origin.url"]) or None
    commit = _git(["rev-parse", "HEAD"]) or None
    return _RepoInfo(url=origin_url, commit=commit)


class ExperimentManager:
    def __init__(self) -> None:
        ensure_config_initialized()
        self._config: KForgeConfig = load_config()
        self._providers: List[Provider] = []

        if self._config.runpod.api_key:
            self._providers.append(RunpodProvider(self._config))
        if self._config.lambdalabs.api_key:
            self._providers.append(LambdaLabsProvider(self._config))

    def list_instances(self) -> List[Instance]:
        instances: List[Instance] = []
        for provider in self._providers:
            instances.extend(provider.list_instances())
        return instances

    def _collect_offers(self) -> list[tuple[Provider, ComputeOffer]]:
        provider_offers: list[tuple[Provider, ComputeOffer]] = []
        for provider in self._providers:
            for offer in provider.get_available_compute():
                provider_offers.append((provider, offer))
        return provider_offers

    def _choose_offer(self, offers: list[tuple[Provider, ComputeOffer]]) -> Tuple[Provider, ComputeOffer]:
        priorities = self._config.preferences.gpu_priority
        if not offers:
            raise RuntimeError("No compute offers available from configured providers.")

        # Rank by priority index (lower is better) then price
        def offer_key(item: tuple[Provider, ComputeOffer]) -> tuple[int, float]:
            _, offer = item
            try:
                priority_index = priorities.index(offer.gpu_type)
            except ValueError:
                priority_index = len(priorities) + 1
            return (priority_index, offer.price_per_hour)

        offers_sorted = sorted(offers, key=offer_key)
        return offers_sorted[0]

    def run_experiment(self, *, branch: str, repo_path: Path) -> str:
        repo = _detect_git_repo_info(repo_path)
        if not self._providers:
            raise RuntimeError("No providers configured. Add API keys to ~/.kforge/config.toml")

        offers = self._collect_offers()
        provider, offer = self._choose_offer(offers)

        return provider.run_experiment(
            branch=branch,
            repo_url=repo.url,
            repo_commit=repo.commit,
            selected_gpu=offer.gpu_type,
        )

    def stop_experiment(self, exp_id: str) -> None:
        # exp_id convention: "provider:inner_id"
        if ":" not in exp_id:
            raise ValueError("Invalid experiment ID. Expected format 'provider:inner_id'")
        provider_name, inner_id = exp_id.split(":", 1)
        for provider in self._providers:
            if provider.name == provider_name:
                provider.stop_instance(inner_id)
                return
        raise RuntimeError(f"Provider not configured: {provider_name}")
