# Generated by Django 4.0 on 2024-03-16 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anime', '0008_alter_anime_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anime',
            name='title',
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
