"""Point d'entrée de l'agent de collecte."""

from __future__ import annotations

import logging
import time

from app.collector import MetricsCollectionError, collect_system_metrics
from app.config import Settings
from app.formatter import format_metrics
from app.sender import MetricsDeliveryError, send_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def run_once(settings: Settings) -> dict:
    """Exécute un cycle complet : collecte, formatage et envoi."""
    metrics = collect_system_metrics()
    payload = format_metrics(metrics)
    return send_metrics(
        endpoint=settings.metrics_endpoint,
        payload=payload,
        timeout=settings.request_timeout,
    )


def run_forever() -> None:
    """Lance l'agent en mode temps réel."""
    settings = Settings.from_env()

    logger.info(
        "Agent démarré. Endpoint=%s, intervalle=%ss",
        settings.metrics_endpoint,
        settings.collection_interval,
    )

    while True:
        try:
            result = run_once(settings)
            logger.info(
                "Métriques envoyées avec succès. HTTP=%s",
                result["status_code"],
            )
        except (
            MetricsCollectionError,
            MetricsDeliveryError,
            ValueError,
        ) as exc:
            logger.error("Cycle échoué : %s", exc)
        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur.")
            break

        time.sleep(settings.collection_interval)


if __name__ == "__main__":
    run_forever()
