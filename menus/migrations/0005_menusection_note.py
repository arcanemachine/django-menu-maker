# Generated by Django 3.1.4 on 2020-12-29 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0004_remove_menusection_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='menusection',
            name='note',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
