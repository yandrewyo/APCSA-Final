# Generated by Django 5.0.3 on 2024-05-20 08:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0003_info_events"),
    ]

    operations = [
        migrations.AlterField(
            model_name="info",
            name="events",
            field=models.JSONField(default=dict),
        ),
    ]
