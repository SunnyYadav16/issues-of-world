"""Source plugins are found by ID through the `iow.sources` entry-point group (pyproject.toml), so the CLI never
imports a plugin module directly. A new plugin is one line in pyproject plus one entry in data/sources.yaml."""

from importlib.metadata import entry_points

from iow.core.contracts import SourcePlugin

GROUP = "iow.sources"


def source_ids() -> list[str]:
    return sorted(ep.name for ep in entry_points(group=GROUP))


def load_source(source_id: str) -> SourcePlugin:
    eps = entry_points(group=GROUP, name=source_id)
    if not eps:
        raise KeyError(f"unknown source {source_id!r}; registered: {source_ids()}")
    return next(iter(eps)).load()()
