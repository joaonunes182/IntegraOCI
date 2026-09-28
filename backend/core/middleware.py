from django.middleware.csrf import CsrfViewMiddleware


class ForceCSRFMiddleware(CsrfViewMiddleware):
    """Verifica CSRF apenas em métodos que alteram dados."""

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return super().process_view(request, callback, callback_args, callback_kwargs)
        return None
