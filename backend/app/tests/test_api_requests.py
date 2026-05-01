"""Tests de los endpoints usando TestClient y override de dependencies."""

from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_approve_use_case,
    get_assign_use_case,
    get_reject_use_case,
)
from app.application.commands import CommandResult
from app.main import app


# ---------------------------------------------------------------------------
# Stubs de casos de uso
# ---------------------------------------------------------------------------

class StubApproveUC:
    def __init__(self, result: CommandResult):
        self.result = result

    def run(self, approval_id, reviewer_id):
        return self.result


class StubRejectUC:
    def __init__(self, result: CommandResult):
        self.result = result

    def run(self, approval_id, reviewer_id, comment):
        return self.result


class StubAssignUC:
    def __init__(self, result: CommandResult):
        self.result = result

    def run(self, request_id, reviewer_id):
        return self.result


client = TestClient(app)
USER_HEADER = {"X-User-Id": str(uuid4())}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_approve_success():
    app.dependency_overrides[get_approve_use_case] = lambda: StubApproveUC(
        CommandResult(success=True, message="ok", data={"new_status": "APPROVED"})
    )
    response = client.post(f"/requests/{uuid4()}/approve", headers=USER_HEADER)
    assert response.status_code == 200
    assert response.json()["new_status"] == "APPROVED"
    app.dependency_overrides.clear()


def test_approve_unauthorized():
    app.dependency_overrides[get_approve_use_case] = lambda: StubApproveUC(
        CommandResult(success=False, message="No autorizado")
    )
    response = client.post(f"/requests/{uuid4()}/approve", headers=USER_HEADER)
    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_approve_without_user_header():
    response = client.post(f"/requests/{uuid4()}/approve")
    assert response.status_code == 401


def test_reject_requires_comment():
    response = client.post(
        f"/requests/{uuid4()}/reject",
        json={"comment": ""},
        headers=USER_HEADER,
    )
    # Pydantic rechaza por min_length=1
    assert response.status_code == 422


def test_reject_success():
    app.dependency_overrides[get_reject_use_case] = lambda: StubRejectUC(
        CommandResult(
            success=True, message="rechazada", data={"new_status": "REJECTED"}
        )
    )
    response = client.post(
        f"/requests/{uuid4()}/reject",
        json={"comment": "Falta plan de rollback"},
        headers=USER_HEADER,
    )
    assert response.status_code == 200
    assert response.json()["new_status"] == "REJECTED"
    app.dependency_overrides.clear()


def test_assign_success():
    app.dependency_overrides[get_assign_use_case] = lambda: StubAssignUC(
        CommandResult(success=True, message="asignado")
    )
    response = client.post(
        f"/requests/{uuid4()}/assign",
        json={"reviewer_id": str(uuid4())},
        headers=USER_HEADER,
    )
    assert response.status_code == 201
    app.dependency_overrides.clear()


def test_assign_not_found():
    app.dependency_overrides[get_assign_use_case] = lambda: StubAssignUC(
        CommandResult(success=False, message="Solicitud no encontrada.")
    )
    response = client.post(
        f"/requests/{uuid4()}/assign",
        json={"reviewer_id": str(uuid4())},
        headers=USER_HEADER,
    )
    assert response.status_code == 404
    app.dependency_overrides.clear()