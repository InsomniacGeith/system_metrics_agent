"""API FastAPI de réception des métriques."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="System Metrics API",
    description="API de réception des métriques envoyées par les agents.",
    version="1.0.0",
)

received_metrics: list[dict[str, Any]] = []


class MetricsPayload(BaseModel):
    """Payload reçu depuis l'agent."""

    agent: str = Field(..., min_length=1)
    event_type: str
    data: dict[str, Any]


@app.get("/metrics")
def get_metrics() -> dict[str, Any]:
    """Retourne toutes les métriques reçues."""
    return {
        "total": len(received_metrics),
        "metrics": received_metrics,
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Vérifie l'état de l'API."""
    return {"status": "ok"}


@app.post("/metrics", status_code=status.HTTP_201_CREATED)
def receive_metrics(payload: MetricsPayload) -> dict[str, Any]:
    """Reçoit et stocke temporairement les métriques."""
    item = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        **payload.model_dump(),
    }
    received_metrics.append(item)

    logger.info(
        "Métriques reçues de %s. Total=%s",
        payload.agent,
        len(received_metrics),
    )

    return {
        "status": "received",
        "message": "Métriques enregistrées avec succès.",
        "total_received": len(received_metrics),
    }


@app.get("/metrics/latest")
def latest_metrics() -> dict[str, Any]:
    """Retourne la dernière métrique reçue."""
    if not received_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune métrique disponible.",
        )

    return received_metrics[-1]
