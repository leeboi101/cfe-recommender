# Generated by Django 4.0 on 2024-03-25 17:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('suggestions', '0002_suggestion_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='suggestion',
            old_name='ratin_value',
            new_name='rating_value',
        ),
    ]
