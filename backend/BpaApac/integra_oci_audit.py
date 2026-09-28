from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from django.utils import timezone

from .models import IntegraOciAuditLog


def _client_ip(request: Any) -> str:
    if not request:
        return ""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return str(forwarded).split(",")[0].strip()
    return str(request.META.get("REMOTE_ADDR") or "").strip()


def _resolve_user_identity(request: Any = None, user: Any = None) -> Dict[str, str]:
    actor = user or getattr(request, "user", None)
    if actor and getattr(actor, "is_authenticated", False):
        display_name = f"{getattr(actor, 'first_name', '')} {getattr(actor, 'last_name', '')}".strip()
        return {
            "username": getattr(actor, "username", "") or "",
            "performed_by": display_name or getattr(actor, "username", "") or "usuario",
        }
    return {"username": "", "performed_by": "sistema"}


def user_has_integra_oci_item(user: Any, item_key: str) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True

    from core.models import GroupModulePermission

    permissions = GroupModulePermission.objects.filter(group__user=user, module_key="integra_oci")
    if not permissions.exists():
        return True

    allowed_permissions = [permission for permission in permissions if permission.can_view or permission.can_do]
    if not allowed_permissions:
        return False

    found_any_item = False
    for permission in allowed_permissions:
        allowed_items = permission.allowed_items or []
        if not allowed_items:
            continue
        found_any_item = True
        if any(str(item.get("item_key") or "") == item_key for item in allowed_items if isinstance(item, dict)):
            return True

    return not found_any_item


def user_has_integra_oci_module(user: Any) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True

    from core.models import GroupModulePermission

    permissions = GroupModulePermission.objects.filter(group__user=user, module_key="integra_oci")
    if not permissions.exists():
        return True
    return any(permission.can_view or permission.can_do for permission in permissions)


def require_integra_oci_item(request: Any, item_key: str, denied_message: str = "Sem permissão para este recurso do Integra OCI."):
    from ninja.errors import HttpError

    user = getattr(request, "user", None) or getattr(request, "auth", None)
    if not user or not getattr(user, "is_authenticated", False):
        raise HttpError(401, "Usuário não autenticado.")
    if not user_has_integra_oci_item(user, item_key):
        raise HttpError(403, denied_message)


def _serialize_json(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if value in (None, ""):
        return {}
    try:
        return json.loads(json.dumps(value, default=str))
    except Exception:
        return {"raw": str(value)}


def log_integra_oci_audit(
    *,
    request: Any = None,
    user: Any = None,
    event_type: str,
    module_item: str = "",
    apac_filename: str = "",
    bpa_filename: str = "",
    extra_files: Optional[List[str]] = None,
    unit_cnes: str = "",
    unit_name: str = "",
    competencias: Optional[List[str]] = None,
    success: bool = True,
    error_message: str = "",
    result_summary: Optional[Dict[str, Any]] = None,
    result_message: str = "",
    history_id: Optional[int] = None,
    history_type: str = "",
) -> IntegraOciAuditLog:
    identity = _resolve_user_identity(request=request, user=user)
    actor = user or getattr(request, "user", None) or getattr(request, "auth", None)

    return IntegraOciAuditLog.objects.create(
        user=actor if actor and getattr(actor, "is_authenticated", False) else None,
        username=identity["username"],
        performed_by=identity["performed_by"],
        event_type=str(event_type or "").strip() or "evento",
        module_item=str(module_item or "").strip(),
        apac_filename=str(apac_filename or "").strip()[:255],
        bpa_filename=str(bpa_filename or "").strip()[:255],
        extra_files=list(extra_files or []),
        unit_cnes=str(unit_cnes or "").strip()[:7],
        unit_name=str(unit_name or "").strip()[:255],
        competencias=list(competencias or []),
        success=bool(success),
        error_message=str(error_message or "").strip(),
        result_summary=_serialize_json(result_summary),
        result_message=str(result_message or "").strip(),
        history_id=history_id,
        history_type=str(history_type or "").strip()[:20],
        ip_address=_client_ip(request),
    )


def serialize_integra_oci_audit_log(entry: IntegraOciAuditLog) -> Dict[str, Any]:
    created_at = entry.created_at
    if timezone.is_naive(created_at):
        created_at = timezone.make_aware(created_at, timezone.get_current_timezone())
    local_created_at = timezone.localtime(created_at)
    return {
        "id": entry.id,
        "username": entry.username,
        "performed_by": entry.performed_by,
        "event_type": entry.event_type,
        "module_item": entry.module_item,
        "apac_filename": entry.apac_filename,
        "bpa_filename": entry.bpa_filename,
        "extra_files": entry.extra_files or [],
        "unit_cnes": entry.unit_cnes,
        "unit_name": entry.unit_name,
        "competencias": entry.competencias or [],
        "success": entry.success,
        "error_message": entry.error_message,
        "result_summary": entry.result_summary or {},
        "result_message": entry.result_message,
        "history_id": entry.history_id,
        "history_type": entry.history_type,
        "ip_address": entry.ip_address,
        "created_at": local_created_at.isoformat(),
        "created_at_label": local_created_at.strftime("%d/%m/%Y %H:%M:%S"),
    }
