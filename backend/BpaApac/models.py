from django.db import models
from django.conf import settings

class BpaApacImportHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    apac_filename = models.CharField(max_length=255, null=True, blank=True)
    bpa_filename = models.CharField(max_length=255, null=True, blank=True)
    unit_cnes = models.CharField(max_length=7, blank=True, default="")
    
    bpa_lines_before = models.IntegerField(default=0)
    bpa_lines_after = models.IntegerField(default=0)
    oci_patients_removed = models.IntegerField(default=0)
    apac_oci_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Import on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')} - Removed: {self.oci_patients_removed}"


class OciComboAnalysisHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    bpa_filename = models.CharField(max_length=255, null=True, blank=True)
    unit_name = models.CharField(max_length=255, blank=True, default="")
    unit_cnes = models.CharField(max_length=7, blank=True, default="")
    competencias = models.JSONField(default=list, blank=True)

    total_patients_analyzed = models.IntegerField(default=0)
    patients_with_combos = models.IntegerField(default=0)
    combo_occurrences = models.IntegerField(default=0)
    combo_types_identified = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OCI {self.created_at.strftime('%Y-%m-%d %H:%M:%S')} - Combos: {self.combo_occurrences}"


class IntegraOciAuditLog(models.Model):
    EVENT_LOGIN = "login"
    EVENT_BPA_PROCESS = "bpa_limpo_process"
    EVENT_BPA_DOWNLOAD = "bpa_limpo_download"
    EVENT_COMBO_VALIDATE = "combo_validate"
    EVENT_COMBO_DOWNLOAD = "combo_download"
    EVENT_FILE_ANALYZE = "file_analyze"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=150, blank=True, default="")
    performed_by = models.CharField(max_length=150, blank=True, default="")
    event_type = models.CharField(max_length=50, db_index=True)
    module_item = models.CharField(max_length=50, blank=True, default="")
    apac_filename = models.CharField(max_length=255, blank=True, default="")
    bpa_filename = models.CharField(max_length=255, blank=True, default="")
    extra_files = models.JSONField(default=list, blank=True)
    unit_cnes = models.CharField(max_length=7, blank=True, default="", db_index=True)
    unit_name = models.CharField(max_length=255, blank=True, default="")
    competencias = models.JSONField(default=list, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, default="")
    result_summary = models.JSONField(default=dict, blank=True)
    result_message = models.TextField(blank=True, default="")
    history_id = models.IntegerField(null=True, blank=True)
    history_type = models.CharField(max_length=20, blank=True, default="")
    ip_address = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["unit_cnes", "created_at"]),
            models.Index(fields=["username", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.performed_by} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
