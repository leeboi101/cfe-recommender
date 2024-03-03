# Generated by Django 4.0 on 2024-03-03 17:35

from django.db import migrations, models
import exports.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Export',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(blank=True, null=True, upload_to=exports.models.export_file_handler)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
