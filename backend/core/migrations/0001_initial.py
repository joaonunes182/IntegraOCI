from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("resource", models.CharField(max_length=100)),
                ("resource_id", models.IntegerField(blank=True, null=True)),
                ("action", models.CharField(max_length=100)),
                ("performed_by", models.CharField(max_length=150)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("details", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Log de Auditoria",
                "verbose_name_plural": "Logs de Auditoria",
                "ordering": ["-timestamp"],
            },
        ),
        migrations.CreateModel(
            name="GroupModulePermission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("module_key", models.CharField(db_index=True, max_length=100)),
                ("can_view", models.BooleanField(default=False)),
                ("can_do", models.BooleanField(default=False)),
                ("allowed_items", models.JSONField(blank=True, default=list)),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="module_permissions",
                        to="auth.group",
                    ),
                ),
            ],
            options={
                "verbose_name": "Permissão de Módulo por Grupo",
                "verbose_name_plural": "Permissões de Módulo por Grupo",
                "unique_together": {("group", "module_key")},
            },
        ),
    ]
