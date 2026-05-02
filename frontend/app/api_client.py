"""Cliente HTTP para consumir la API de ChangeFlow desde Streamlit."""

import os
from typing import Optional
from uuid import UUID

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")


class ApiClient:
    """
    Wrapper sobre requests que añade el header X-User-Id (placeholder de auth)
    y centraliza el manejo de errores.
    """

    def __init__(self, user_id: UUID, base_url: str = API_BASE_URL):
        self.user_id = user_id
        self.base_url = base_url

    def _headers(self) -> dict:
        return {"X-User-Id": str(self.user_id)}

    def approve(self, approval_id: UUID) -> tuple[bool, str, Optional[dict]]:
        url = f"{self.base_url}/requests/{approval_id}/approve"
        resp = requests.post(url, headers=self._headers(), timeout=10)
        return self._parse(resp)

    def reject(
        self, approval_id: UUID, comment: str
    ) -> tuple[bool, str, Optional[dict]]:
        url = f"{self.base_url}/requests/{approval_id}/reject"
        resp = requests.post(
            url,
            headers=self._headers(),
            json={"comment": comment},
            timeout=10,
        )
        return self._parse(resp)

    def assign_reviewer(
        self, request_id: UUID, reviewer_id: UUID
    ) -> tuple[bool, str, Optional[dict]]:
        url = f"{self.base_url}/requests/{request_id}/assign"
        resp = requests.post(
            url,
            headers=self._headers(),
            json={"reviewer_id": str(reviewer_id)},
            timeout=10,
        )
        return self._parse(resp)

    @staticmethod
    def _parse(resp: requests.Response) -> tuple[bool, str, Optional[dict]]:
        try:
            data = resp.json()
        except ValueError:
            data = {}
        if 200 <= resp.status_code < 300:
            return True, data.get("message", "OK"), data
        return False, data.get("detail", f"Error HTTP {resp.status_code}"), data