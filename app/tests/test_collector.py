from unittest.mock import Mock, patch

import pytest

from app.collector import (
    MetricsCollectionError,
    collect_system_metrics,
    get_load_average,
)


@patch("app.collector.subprocess.run")
def test_get_load_average_success(mock_run):
    mock_run.return_value = Mock(
        stdout=" 10:00:00 up 2 days, load average: 0.10, 0.20, 0.30\n"
    )

    result = get_load_average()

    assert result == {
        "load_1m": 0.10,
        "load_5m": 0.20,
        "load_15m": 0.30,
    }


@patch("app.collector.subprocess.run")
def test_get_load_average_command_error(mock_run):
    mock_run.side_effect = FileNotFoundError("uptime absent")

    with pytest.raises(MetricsCollectionError):
        get_load_average()


@patch("app.collector.get_load_average")
@patch("app.collector.psutil.cpu_percent")
@patch("app.collector.psutil.cpu_count")
@patch("app.collector.psutil.virtual_memory")
def test_collect_system_metrics(
    mock_memory,
    mock_cpu_count,
    mock_cpu_percent,
    mock_load,
):
    mock_memory.return_value = Mock(
        total=1000,
        available=400,
        used=600,
        percent=60.0,
    )
    mock_cpu_percent.return_value = 25.5
    mock_cpu_count.return_value = 8
    mock_load.return_value = {
        "load_1m": 0.1,
        "load_5m": 0.2,
        "load_15m": 0.3,
    }

    metrics = collect_system_metrics()

    assert metrics["cpu"]["percent"] == 25.5
    assert metrics["cpu"]["logical_cores"] == 8
    assert metrics["memory"]["percent"] == 60.0
    assert metrics["system"]["load_1m"] == 0.1
    assert "timestamp" in metrics
