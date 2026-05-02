"""Rutas de auditoría: GET /audit, GET /audit/{entity_type}/{entity_id}."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_audit_repo, get_current_user
from app.api.schemas import AuditEntryResponse
from app.infrastructure.repositories.audit_repository import SQLAlchemyAuditRepository

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=List[AuditEntryResponse])
def list_audit_log(
    current_user: dict = Depends(get_current_user),
    repo: SQLAlchemyAuditRepository = Depends(get_audit_repo),
):
    """Devuelve todo el log de auditoría ordenado por fecha desc. Solo para Admin."""
    entries = repo.list_all()
    return [
        AuditEntryResponse(
            id=e.id,
            actor_id=e.actor_id,
            action=e.action,
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            detail=e.detail,
            occurred_at=e.occurred_at,
        )
        for e in entries
    ]


@router.get("/{entity_type}/{entity_id}", response_model=List[AuditEntryResponse])
def list_audit_for_entity(
    entity_type: str,
    entity_id: str,
    current_user: dict = Depends(get_current_user),
    repo: SQLAlchemyAuditRepository = Depends(get_audit_repo),
):
    """Devuelve el historial de auditoría de una entidad específica (ej. ChangeRequest)."""
    entries = repo.list_for_entity(entity_type, entity_id)
    return [
        AuditEntryResponse(
            id=e.id,
            actor_id=e.actor_id,
            action=e.action,
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            detail=e.detail,
            occurred_at=e.occurred_at,
        )
        for e in entries
    ]
