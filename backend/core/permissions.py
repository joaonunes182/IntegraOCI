"""
Catálogo de permissões do IntegraOCI standalone.

Define os módulos e itens de permissão disponíveis nesta aplicação.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Catálogo de módulos
# ---------------------------------------------------------------------------

MODULE_PERMISSION_CATALOG: list[dict] = [
    {
        "key": "integra_oci",
        "name": "Integra OCI",
        "description": "Importação, análise de BPA/APAC e painel analítico.",
        "sort_order": 10,
    },
    {
        "key": "gerenciador_usuarios",
        "name": "Gerenciador de Usuários",
        "description": "Cadastro, edição e ativação de usuários.",
        "sort_order": 20,
    },
    {
        "key": "gerenciador_perfis",
        "name": "Perfis e Permissões",
        "description": "Configuração de grupos e permissões.",
        "sort_order": 30,
    },
    {
        "key": "auditoria",
        "name": "Auditoria",
        "description": "Consulta aos eventos de auditoria.",
        "sort_order": 40,
    },
]

# ---------------------------------------------------------------------------
# Itens de permissão por módulo
# ---------------------------------------------------------------------------

MODULE_ALLOWED_ITEM_CATALOG: dict[str, dict] = {
    "integra_oci": {
        "bpa_limpo": {
            "item_name": "BPA Inteligente (BPA Tratado)",
            "category": "Integra OCI",
        },
        "formar_combos": {
            "item_name": "Validação de Combos",
            "category": "Integra OCI",
        },
        "dashboard": {
            "item_name": "Dashboard Analítico",
            "category": "Integra OCI",
        },
        "historico": {
            "item_name": "Histórico e Exportações",
            "category": "Integra OCI",
        },
        "auditoria": {
            "item_name": "Auditoria",
            "category": "Integra OCI",
        },
    },
}


def get_module_permission_catalog() -> list[dict]:
    """Retorna o catálogo de módulos ordenado por sort_order."""
    return sorted(MODULE_PERMISSION_CATALOG, key=lambda item: item["sort_order"])
