"""Tests del cliente HTTP del frontend."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.api_client import ApiClient


@patch("app.api_client.requests.post")
def test_approve_success(mock_post):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"message": "ok", "new_status": "APPROVED"},
    )
    client = ApiClient(user_id=uuid4())
    ok, msg, data = client.approve(uuid4())
    assert ok is True
    assert msg == "ok"


@patch("app.api_client.requests.post")
def test_approve_unauthorized(mock_post):
    mock_post.return_value = MagicMock(
        status_code=403,
        json=lambda: {"detail": "No autorizado"},
    )
    client = ApiClient(user_id=uuid4())
    ok, msg, _ = client.approve(uuid4())
    assert ok is False
    assert "autorizado" in msg.lower()


@patch("app.api_client.requests.post")
def test_reject_sends_comment(mock_post):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"message": "rechazada"},
    )
    client = ApiClient(user_id=uuid4())
    client.reject(uuid4(), comment="Falta plan de rollback")
    # Verificar que el comentario viajó en el body
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["comment"] == "Falta plan de rollback"


@patch("app.api_client.requests.post")
def test_assign_reviewer(mock_post):
    mock_post.return_value = MagicMock(
        status_code=201,
        json=lambda: {"message": "asignado"},
    )
    client = ApiClient(user_id=uuid4())
    ok, _, _ = client.assign_reviewer(uuid4(), uuid4())
    assert ok is True