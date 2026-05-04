"""Cliente HTTP para consumir la API de ChangeFlow desde Streamlit."""

import os
from datetime import datetime
from typing import Optional
from uuid import UUID

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")


class ApiClient:
    """Wrapper sobre requests. Usa X-User-Id como auth simple para acciones de
    flujo y, opcionalmente, Bearer token para endpoints autenticados."""

    def __init__(self, user_id: UUID, token: str | None = None, base_url: str = API_BASE_URL):
        self.user_id = user_id
        self.token = token
        self.base_url = base_url

    def _headers(self) -> dict:
        h = {"X-User-Id": str(self.user_id)}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    # ----- CRUD -----
    def list_requests(self) -> tuple[bool, str, Optional[list]]:
        resp = requests.get(f"{self.base_url}/requests/", headers=self._headers(), timeout=10)
        return self._parse_list(resp)

    def get_request(self, request_id: UUID):
        resp = requests.get(f"{self.base_url}/requests/{request_id}", headers=self._headers(), timeout=10)
        return self._parse(resp)

    def create_request(self, payload: dict):
        resp = requests.post(f"{self.base_url}/requests/", headers=self._headers(), json=payload, timeout=10)
        return self._parse(resp)

    # ----- Flow -----
    def submit(self, request_id: UUID):
        return self._parse(requests.post(f"{self.base_url}/requests/{request_id}/submit", headers=self._headers(), timeout=10))

    def approve(self, approval_id: UUID):
        return self._parse(requests.post(f"{self.base_url}/requests/{approval_id}/approve", headers=self._headers(), timeout=10))

    def reject(self, approval_id: UUID, comment: str):
        return self._parse(requests.post(
            f"{self.base_url}/requests/{approval_id}/reject",
            headers=self._headers(), json={"comment": comment}, timeout=10,
        ))

    def request_changes(self, approval_id: UUID, comment: str):
        return self._parse(requests.post(
            f"{self.base_url}/requests/{approval_id}/request-changes",
            headers=self._headers(), json={"comment": comment}, timeout=10,
        ))

    def assign_reviewer(self, request_id: UUID, reviewer_id: UUID):
        return self._parse(requests.post(
            f"{self.base_url}/requests/{request_id}/assign",
            headers=self._headers(), json={"reviewer_id": str(reviewer_id)}, timeout=10,
        ))

    def cancel(self, request_id: UUID):
        return self._parse(requests.post(f"{self.base_url}/requests/{request_id}/cancel", headers=self._headers(), timeout=10))

    def schedule(self, request_id: UUID, scheduled_at: datetime):
        return self._parse(requests.post(
            f"{self.base_url}/requests/{request_id}/schedule",
            headers=self._headers(), json={"scheduled_at": scheduled_at.isoformat()}, timeout=10,
        ))

    def execute(self, request_id: UUID):
        return self._parse(requests.post(f"{self.base_url}/requests/{request_id}/execute", headers=self._headers(), timeout=10))

    def fail(self, request_id: UUID, reason: str):
        return self._parse(requests.post(
            f"{self.base_url}/requests/{request_id}/fail",
            headers=self._headers(), json={"reason": reason}, timeout=10,
        ))

    @staticmethod
    def _parse(resp: requests.Response) -> tuple[bool, str, Optional[dict]]:
        try:
            data = resp.json()
        except ValueError:
            data = {}
        if 200 <= resp.status_code < 300:
            return True, data.get("message", "OK") if isinstance(data, dict) else "OK", data
        if isinstance(data, dict):
            return False, data.get("detail", f"Error HTTP {resp.status_code}"), data
        return False, f"Error HTTP {resp.status_code}", None

    @staticmethod
    def _parse_list(resp: requests.Response):
        if 200 <= resp.status_code < 300:
            return True, "OK", resp.json()
        try:
            d = resp.json()
            return False, d.get("detail", f"Error HTTP {resp.status_code}"), None
        except ValueError:
            return False, f"Error HTTP {resp.status_code}", None
