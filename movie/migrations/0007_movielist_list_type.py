# Generated by Django 2.2.10 on 2025-02-16 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0006_auto_20250215_0047'),
    ]

    operations = [
        migrations.AddField(
            model_name='movielist',
            name='list_type',
            field=models.CharField(default='精选影单', max_length=255, verbose_name='影单类型'),
        ),
    ]
