# Generated by Django 5.0.7 on 2024-07-29 10:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maills", "0006_alter_message_files"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="message_id",
            field=models.CharField(default=2, max_length=255),
            preserve_default=False,
        ),
    ]
