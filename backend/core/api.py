"""
API de autenticação do IntegraOCI standalone.

Fornece endpoints de login (JWT via cookie), refresh, dados do usuário
e permissões de módulo.
"""

from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from ninja.responses import JsonResponse
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from decouple import config

from core.auth import JWTCookieAuth
from core.models import GroupModulePermission
from BpaApac.integra_oci_audit import log_integra_oci_audit, user_has_integra_oci_module

# Todos os itens do módulo integra_oci disponíveis nesta aplicação
_INTEGRA_OCI_ITEMS = ["bpa_limpo", "formar_combos", "dashboard", "historico", "auditoria"]

User = get_user_model()
TOKEN_EXPIRATION_TIME = config("TOKEN_EXPIRATION_TIME", default=86400, cast=int)

api_auth = NinjaAPI(title="IntegraOCI Auth", urls_namespace="auth", auth=JWTCookieAuth())


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class LoginSchema(Schema):
    username: str
    password: str


class UserSchema(Schema):
    username: str
    email: str
    first_name: str
    last_name: str
    is_staff: bool
    is_superuser: bool


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@api_auth.post("/", auth=None)
def login(request, data: LoginSchema):
    """
    Autentica o usuário e emite cookies JWT (access_token + refresh_token).
    """
    user = User.objects.filter(username=data.username).first()
    if user is None:
        user = User.objects.filter(email=data.username).first()
    if user is None:
        return JsonResponse({"error": "Usuário não encontrado"}, status=404)

    if not user.is_active:
        return JsonResponse({"error": "Usuário inativo. Contate o administrador."}, status=403)

    user = authenticate(request, username=user.username, password=data.password)
    if user is None:
        return JsonResponse({"error": "Senha inválida"}, status=401)

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    response = JsonResponse({
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    })
    response["Access-Control-Allow-Credentials"] = "true"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=TOKEN_EXPIRATION_TIME,
    )
    response.set_cookie(
        key="refresh_token",
        value=str(refresh),
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=86400,
    )

    # Auditoria de login no IntegraOCI
    try:
        if user_has_integra_oci_module(user):
            log_integra_oci_audit(
                request=request,
                user=user,
                event_type="login",
                module_item="sistema",
                result_message="Login realizado com acesso ao Integra OCI.",
                result_summary={"email": user.email or ""},
            )
    except Exception:
        pass

    return response


@api_auth.post("/refresh/", auth=None)
def refresh_token(request):
    """Renova o access_token usando o refresh_token do cookie."""
    refresh_cookie = request.COOKIES.get("refresh_token")
    if not refresh_cookie:
        return JsonResponse({"error": "Token de refresh não encontrado."}, status=401)
    try:
        refresh = RefreshToken(refresh_cookie)
        new_access = str(refresh.access_token)
    except Exception:
        return JsonResponse({"error": "Token de refresh inválido ou expirado."}, status=401)

    response = JsonResponse({"detail": "Token renovado."})
    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=TOKEN_EXPIRATION_TIME,
    )
    return response


@api_auth.post("/logout/")
def logout(request):
    """Remove os cookies JWT."""
    response = JsonResponse({"detail": "Logout realizado."})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@api_auth.get("/user/", response=UserSchema)
def get_user(request):
    """Retorna dados do usuário autenticado."""
    user = getattr(request, "user", None) or getattr(request, "auth", None)
    if not user or not user.is_authenticated:
        raise HttpError(401, "Usuário não autenticado.")
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    }


@api_auth.get("/permissions/")
def get_permissions(request):
    """
    Retorna as permissões de módulo do usuário autenticado.

    Superusuários e staff recebem acesso total a todos os itens.
    Usuários comuns recebem as permissões configuradas via GroupModulePermission.
    Se nenhuma permissão estiver configurada, todos os itens são liberados
    (comportamento padrão aberto, igual ao backend).
    """
    user = getattr(request, "user", None) or getattr(request, "auth", None)
    if not user or not user.is_authenticated:
        raise HttpError(401, "Usuário não autenticado.")

    # Superuser/staff → acesso total a tudo
    if user.is_superuser or user.is_staff:
        all_items = [{"item_key": k} for k in _INTEGRA_OCI_ITEMS]
        return {
            "integra_oci": {
                "can_view": True,
                "can_do": True,
                "allowed": True,
                "allowed_items": all_items,
            }
        }

    # Busca permissões configuradas por grupo
    group_perms = GroupModulePermission.objects.filter(
        group__user=user,
        module_key="integra_oci",
    )

    if not group_perms.exists():
        # Sem restrições configuradas → libera tudo (padrão aberto)
        all_items = [{"item_key": k} for k in _INTEGRA_OCI_ITEMS]
        return {
            "integra_oci": {
                "can_view": True,
                "can_do": True,
                "allowed": True,
                "allowed_items": all_items,
            }
        }

    # Agrega permissões de todos os grupos do usuário
    can_view = any(p.can_view for p in group_perms)
    can_do = any(p.can_do for p in group_perms)

    if not can_view and not can_do:
        return {
            "integra_oci": {
                "can_view": False,
                "can_do": False,
                "allowed": False,
                "allowed_items": [],
            }
        }

    # Agrega allowed_items de todos os grupos
    seen = set()
    allowed_items = []
    for perm in group_perms:
        if not (perm.can_view or perm.can_do):
            continue
        items = perm.allowed_items or []
        if not items:
            # Grupo sem restrição de itens → libera todos
            all_items = [{"item_key": k} for k in _INTEGRA_OCI_ITEMS]
            return {
                "integra_oci": {
                    "can_view": can_view,
                    "can_do": can_do,
                    "allowed": True,
                    "allowed_items": all_items,
                }
            }
        for item in items:
            key = item.get("item_key", "") if isinstance(item, dict) else str(item)
            if key and key not in seen:
                seen.add(key)
                allowed_items.append({"item_key": key})

    return {
        "integra_oci": {
            "can_view": can_view,
            "can_do": can_do,
            "allowed": can_view or can_do,
            "allowed_items": allowed_items,
        }
    }
