# Generated by Django 3.1.2 on 2020-10-25 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0006_auto_20201025_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='slug',
            field=models.SlugField(default=None, max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='menusection',
            name='slug',
            field=models.SlugField(default=None, max_length=128),
            preserve_default=False,
        ),
    ]
