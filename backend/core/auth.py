"""
Autenticação JWT via cookie para o IntegraOCI standalone.

Replica o JWTCookieAuth do Portal-SCCS de forma independente,
sem nenhuma dependência do projeto original.
"""

from ninja.security import APIKeyCookie
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


class JWTCookieAuth(APIKeyCookie):
    """Autenticação via cookie `access_token` (JWT SimpleJWT)."""

    param_name = "access_token"

    def authenticate(self, request, key):
        if not key:
            return None
        try:
            access_token = AccessToken(key)
            user = User.objects.get(id=access_token["user_id"])
            request.user = user
            return user
        except Exception as e:
            print("Erro na autenticação via cookie:", e)
            return None
