# Generated by Django 3.1.4 on 2020-12-29 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0007_auto_20201229_0726'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='description',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
