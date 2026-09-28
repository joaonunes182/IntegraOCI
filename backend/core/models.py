"""
Modelos de suporte do IntegraOCI standalone.

- AuditLog: trilha de auditoria geral (equivalente ao Audit.Audit do Portal-SCCS)
- GroupModulePermission: controle granular de permissões de módulos por grupo
                         (equivalente ao Profile.GroupModulePermission do Portal-SCCS)
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group


class AuditLog(models.Model):
    """Registro geral de auditoria do sistema."""

    resource = models.CharField(max_length=100)
    resource_id = models.IntegerField(null=True, blank=True)
    action = models.CharField(max_length=100)
    performed_by = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"

    def __str__(self):
        return f"{self.resource} {self.action} por {self.performed_by} em {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


class GroupModulePermission(models.Model):
    """
    Permissão granular de módulo por grupo.

    Replica a estrutura do Portal-SCCS para controle de acesso ao
    módulo integra_oci e seus itens (bpa_limpo, formar_combos, etc.).
    """

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="module_permissions")
    module_key = models.CharField(max_length=100, db_index=True)
    can_view = models.BooleanField(default=False)
    can_do = models.BooleanField(default=False)
    allowed_items = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = [("group", "module_key")]
        verbose_name = "Permissão de Módulo por Grupo"
        verbose_name_plural = "Permissões de Módulo por Grupo"

    def __str__(self):
        return f"{self.group.name} — {self.module_key}"
