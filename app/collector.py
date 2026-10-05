"""Module de collecte des métriques système."""

from __future__ import annotations

import platform
import subprocess
from datetime import datetime, timezone
from typing import Any

import psutil


class MetricsCollectionError(RuntimeError):
    """Erreur levée lorsqu'une métrique ne peut pas être collectée."""


def get_load_average() -> dict[str, float | None]:
    """Retourne la charge système via subprocess.

    La commande `uptime` est exécutée afin de démontrer une collecte
    complémentaire basée sur un processus système externe. La valeur est
    disponible principalement sur les systèmes Unix.
    """
    if platform.system().lower().startswith("win"):
        return {
            "load_1m": None,
            "load_5m": None,
            "load_15m": None,
        }

    try:
        result = subprocess.run(
            ["uptime"],
            capture_output=True,
            text=True,
            check=True,
            timeout=3,
        )
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ) as exc:
        raise MetricsCollectionError(
            f"Impossible d'exécuter la commande uptime : {exc}"
        ) from exc

    output = result.stdout.strip()

    try:
        marker = "load average:"
        if marker not in output:
            marker = "load averages:"
        values = output.split(marker, maxsplit=1)[1].strip()
        values = values.replace(",", " ")
        parts = [float(value.strip()) for value in values.split()[:3]]
        if len(parts) != 3:
            raise ValueError("Nombre de valeurs insuffisant.")
    except (IndexError, ValueError) as exc:
        raise MetricsCollectionError(
            f"Impossible d'analyser la sortie uptime : {output}"
        ) from exc

    return {
        "load_1m": parts[0],
        "load_5m": parts[1],
        "load_15m": parts[2],
    }


def collect_system_metrics() -> dict[str, Any]:
    """Collecte les métriques CPU, RAM et la charge système."""
    try:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        load_average = get_load_average()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hostname": platform.node(),
            "cpu": {
                "percent": cpu_percent,
                "logical_cores": psutil.cpu_count(logical=True),
            },
            "memory": {
                "total_bytes": memory.total,
                "available_bytes": memory.available,
                "used_bytes": memory.used,
                "percent": memory.percent,
            },
            "system": load_average,
        }
    except MetricsCollectionError:
        raise
    except Exception as exc:
        raise MetricsCollectionError(
            f"Erreur pendant la collecte des métriques : {exc}"
        ) from exc
