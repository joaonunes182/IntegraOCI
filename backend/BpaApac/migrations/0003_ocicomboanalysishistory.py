from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("BpaApac", "0002_bpaapacimporthistory_apac_filename_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="OciComboAnalysisHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("bpa_filename", models.CharField(blank=True, max_length=255, null=True)),
                ("unit_name", models.CharField(blank=True, default="", max_length=255)),
                ("unit_cnes", models.CharField(blank=True, default="", max_length=7)),
                ("competencias", models.JSONField(blank=True, default=list)),
                ("total_patients_analyzed", models.IntegerField(default=0)),
                ("patients_with_combos", models.IntegerField(default=0)),
                ("combo_occurrences", models.IntegerField(default=0)),
                ("combo_types_identified", models.IntegerField(default=0)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
