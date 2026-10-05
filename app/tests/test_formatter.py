import pytest

from app.formatter import format_metrics


def valid_metrics():
    return {
        "timestamp": "2026-08-27T12:00:00+00:00",
        "hostname": "test-host",
        "cpu": {"percent": 10.0},
        "memory": {"percent": 20.0},
        "system": {"load_1m": 0.1},
    }


def test_format_metrics_success():
    payload = format_metrics(valid_metrics())

    assert payload["agent"] == "system-metrics-agent"
    assert payload["event_type"] == "system_metrics"
    assert payload["data"]["hostname"] == "test-host"


def test_format_metrics_missing_key():
    metrics = valid_metrics()
    del metrics["cpu"]

    with pytest.raises(ValueError, match="Clés manquantes"):
        format_metrics(metrics)
