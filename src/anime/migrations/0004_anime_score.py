# Generated by Django 4.0 on 2024-03-07 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anime', '0003_anime_rating_avg_anime_rating_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='anime',
            name='score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
