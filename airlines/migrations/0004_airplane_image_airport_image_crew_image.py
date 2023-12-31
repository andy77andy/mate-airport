# Generated by Django 4.2.4 on 2023-08-18 12:09

import airlines.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("airlines", "0003_flight_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="airplane",
            name="image",
            field=models.ImageField(
                null=True, upload_to=airlines.models.image_file_path
            ),
        ),
        migrations.AddField(
            model_name="airport",
            name="image",
            field=models.ImageField(
                null=True, upload_to=airlines.models.image_file_path
            ),
        ),
        migrations.AddField(
            model_name="crew",
            name="image",
            field=models.ImageField(
                null=True, upload_to=airlines.models.image_file_path
            ),
        ),
    ]
