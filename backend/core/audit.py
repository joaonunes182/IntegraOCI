"""
Utilitário de auditoria geral do IntegraOCI standalone.

Replica o Audit.utils.log_audit_event do Portal-SCCS de forma
independente, registrando eventos no modelo AuditLog local.
"""

from __future__ import annotations

from typing import Any

from .models import AuditLog


def _resolve_actor_name(request: Any = None, user: Any = None, performed_by: str = "") -> str:
    explicit_name = str(performed_by or "").strip()
    if explicit_name:
        return explicit_name

    request_user = getattr(request, "user", None)
    actor = user or request_user
    if actor and getattr(actor, "is_authenticated", False):
        full_name = f"{getattr(actor, 'first_name', '')} {getattr(actor, 'last_name', '')}".strip()
        return full_name or getattr(actor, "username", "") or "sistema"

    header_name = str(
        getattr(getattr(request, "headers", {}), "get", lambda *_a, **_kw: "")("X-USER-NAME") or ""
    ).strip()
    if header_name:
        return header_name

    return "sistema"


def log_audit_event(
    *,
    resource: str,
    action: str,
    request: Any = None,
    user: Any = None,
    resource_id: int | None = None,
    details: str = "",
    performed_by: str = "",
) -> AuditLog:
    return AuditLog.objects.create(
        resource=str(resource or "").strip() or "sistema",
        resource_id=resource_id,
        action=str(action or "").strip() or "acao nao informada",
        performed_by=_resolve_actor_name(request=request, user=user, performed_by=performed_by),
        details=str(details or "").strip(),
    )
