# Generated by Django 5.0.7 on 2024-07-28 12:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maills", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Email",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("email", models.CharField(max_length=255)),
                ("password", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("emails", models.ManyToManyField(to="maills.email")),
            ],
        ),
    ]
