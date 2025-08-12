from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import ensure_config_initialized
from .core.manager import ExperimentManager

app = typer.Typer(help="KForge: One-line orchestration of ML experiments on remote compute.")
console = Console()


# @app.callback()
# def _init(_: Optional[bool] = typer.Option(None, "--init", help="Initialize ~/.kforge config and exit")) -> None:
#     if _ is not None:
#         ensure_config_initialized()
#         raise typer.Exit(code=0)


@app.command()
def ls() -> None:
    """List running remote instances across all configured providers."""
    ensure_config_initialized()

    manager = ExperimentManager()
    instances = manager.list_instances()

    if not instances:
        console.print("[yellow]No running instances found[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Provider")
    table.add_column("Status")
    table.add_column("GPU")

    for inst in instances:
        table.add_row(inst.id, inst.name or "-", inst.provider, inst.status, inst.gpu_type or "-")

    console.print(table)


@app.command()
def run(branch: str = typer.Argument(..., help="Git branch to run from current repository.")) -> None:
    """Run an experiment from the current repo on remote compute."""
    ensure_config_initialized()

    repo_path = Path.cwd()
    manager = ExperimentManager()
    exp_id = manager.run_experiment(branch=branch, repo_path=repo_path)
    console.print(f"[green]Submitted experiment[/green]: {exp_id}")


@app.command()
def stop(exp_id: str = typer.Argument(..., help="Experiment ID to stop (e.g. runpod:12345)")) -> None:
    """Stop a running experiment by ID."""
    ensure_config_initialized()

    manager = ExperimentManager()
    manager.stop_experiment(exp_id)
    console.print(f"[green]Stopped[/green] {exp_id}")


def main() -> None:
    app()
