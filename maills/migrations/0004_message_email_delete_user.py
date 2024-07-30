# Generated by Django 5.0.7 on 2024-07-28 12:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maills", "0003_email_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="email",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="maills.email",
            ),
        ),
        migrations.DeleteModel(
            name="User",
        ),
    ]