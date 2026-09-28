from django.contrib import admin
from .models import AuditLog, GroupModulePermission


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("resource", "action", "performed_by", "timestamp")
    list_filter = ("resource", "action")
    search_fields = ("resource", "action", "performed_by", "details")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)


@admin.register(GroupModulePermission)
class GroupModulePermissionAdmin(admin.ModelAdmin):
    list_display = ("group", "module_key", "can_view", "can_do")
    list_filter = ("module_key", "can_view", "can_do")
    search_fields = ("group__name", "module_key")
