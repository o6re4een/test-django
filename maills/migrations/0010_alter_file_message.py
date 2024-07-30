# Generated by Django 5.0.7 on 2024-07-29 19:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maills", "0009_remove_message_files_file_message"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="message",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="maills.message",
            ),
        ),
    ]