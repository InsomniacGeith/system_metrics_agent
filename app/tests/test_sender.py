from unittest.mock import Mock, patch

import pytest
import requests

from app.sender import MetricsDeliveryError, send_metrics


@patch("app.sender.requests.post")
def test_send_metrics_success(mock_post):
    response = Mock()
    response.status_code = 201
    response.json.return_value = {"status": "received"}
    response.raise_for_status.return_value = None
    mock_post.return_value = response

    result = send_metrics(
        "http://localhost:8000/metrics",
        {"agent": "test"},
    )

    assert result["status_code"] == 201
    assert result["response"]["status"] == "received"


@patch("app.sender.requests.post")
def test_send_metrics_network_error(mock_post):
    mock_post.side_effect = requests.ConnectionError("API indisponible")

    with pytest.raises(MetricsDeliveryError):
        send_metrics(
            "http://localhost:8000/metrics",
            {"agent": "test"},
        )


@patch("app.sender.requests.post")
def test_send_metrics_http_error(mock_post):
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError("500")
    mock_post.return_value = response

    with pytest.raises(MetricsDeliveryError):
        send_metrics(
            "http://localhost:8000/metrics",
            {"agent": "test"},
        )
