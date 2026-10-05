"""Module d'envoi des métriques vers une API ou un webhook."""

from __future__ import annotations

from typing import Any

import requests


class MetricsDeliveryError(RuntimeError):
    """Erreur levée lorsqu'un envoi HTTP échoue."""


def send_metrics(
    endpoint: str,
    payload: dict[str, Any],
    timeout: float = 5,
) -> dict[str, Any]:
    """Envoie les métriques au format JSON.

    Returns:
        Un résumé de la réponse HTTP.

    Raises:
        MetricsDeliveryError: si l'API est indisponible ou retourne une erreur.
    """
    try:
        response = requests.post(
            endpoint,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise MetricsDeliveryError(f"Échec de l'envoi vers {endpoint} : {exc}") from exc

    try:
        body: Any = response.json()
    except ValueError:
        body = response.text

    return {
        "status_code": response.status_code,
        "response": body,
    }
