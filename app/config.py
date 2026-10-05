"""Chargement de la configuration externe."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Configuration de l'application."""

    metrics_endpoint: str
    collection_interval: float
    request_timeout: float

    @classmethod
    def from_env(cls) -> "Settings":
        endpoint = os.getenv(
            "METRICS_ENDPOINT",
            "http://127.0.0.1:8000/metrics",
        )

        try:
            interval = float(os.getenv("COLLECTION_INTERVAL", "5"))
            timeout = float(os.getenv("REQUEST_TIMEOUT", "5"))
        except ValueError as exc:
            raise ValueError(
                "COLLECTION_INTERVAL et REQUEST_TIMEOUT doivent être numériques."
            ) from exc

        if interval <= 0 or timeout <= 0:
            raise ValueError("COLLECTION_INTERVAL et REQUEST_TIMEOUT doivent être > 0.")

        return cls(
            metrics_endpoint=endpoint,
            collection_interval=interval,
            request_timeout=timeout,
        )
