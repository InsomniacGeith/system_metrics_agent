"""Module de formatage des métriques."""

from __future__ import annotations

from typing import Any


def format_metrics(
    metrics: dict[str, Any],
    agent_name: str = "system-metrics-agent",
) -> dict[str, Any]:
    """Prépare les métriques dans un payload standardisé."""
    required_keys = {"timestamp", "hostname", "cpu", "memory", "system"}
    missing = required_keys.difference(metrics)

    if missing:
        raise ValueError(f"Métriques incomplètes. Clés manquantes : {sorted(missing)}")

    return {
        "agent": agent_name,
        "event_type": "system_metrics",
        "data": metrics,
    }
