# Generated by Django 4.0 on 2024-02-24 01:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rating',
            options={'ordering': ['-timestamps']},
        ),
    ]