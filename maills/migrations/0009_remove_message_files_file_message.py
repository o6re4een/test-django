# Generated by Django 5.0.7 on 2024-07-29 19:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maills", "0008_alter_message_date_got_alter_message_date_sent"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="message",
            name="files",
        ),
        migrations.AddField(
            model_name="file",
            name="message",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="maills.message",
            ),
        ),
    ]