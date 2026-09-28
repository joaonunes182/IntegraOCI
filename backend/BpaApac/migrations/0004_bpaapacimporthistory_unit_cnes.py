from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("BpaApac", "0003_ocicomboanalysishistory"),
    ]

    operations = [
        migrations.AddField(
            model_name="bpaapacimporthistory",
            name="unit_cnes",
            field=models.CharField(blank=True, default="", max_length=7),
        ),
    ]
