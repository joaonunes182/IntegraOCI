from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("BpaApac", "0004_bpaapacimporthistory_unit_cnes"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="IntegraOciAuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(blank=True, default="", max_length=150)),
                ("performed_by", models.CharField(blank=True, default="", max_length=150)),
                ("event_type", models.CharField(db_index=True, max_length=50)),
                ("module_item", models.CharField(blank=True, default="", max_length=50)),
                ("apac_filename", models.CharField(blank=True, default="", max_length=255)),
                ("bpa_filename", models.CharField(blank=True, default="", max_length=255)),
                ("extra_files", models.JSONField(blank=True, default=list)),
                ("unit_cnes", models.CharField(blank=True, db_index=True, default="", max_length=7)),
                ("unit_name", models.CharField(blank=True, default="", max_length=255)),
                ("competencias", models.JSONField(blank=True, default=list)),
                ("success", models.BooleanField(default=True)),
                ("error_message", models.TextField(blank=True, default="")),
                ("result_summary", models.JSONField(blank=True, default=dict)),
                ("result_message", models.TextField(blank=True, default="")),
                ("history_id", models.IntegerField(blank=True, null=True)),
                ("history_type", models.CharField(blank=True, default="", max_length=20)),
                ("ip_address", models.CharField(blank=True, default="", max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["event_type", "created_at"], name="bpaapac_int_event_t_0f0f0f_idx"),
                    models.Index(fields=["unit_cnes", "created_at"], name="bpaapac_int_unit_cn_1a1a1a_idx"),
                    models.Index(fields=["username", "created_at"], name="bpaapac_int_usernam_2b2b2b_idx"),
                ],
            },
        ),
    ]
