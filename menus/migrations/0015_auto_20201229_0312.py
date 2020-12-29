# Generated by Django 3.1.4 on 2020-12-29 03:12

from django.db import migrations, models
import menus.models


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0014_auto_20201228_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(blank=True, help_text='An image or logo for this menu (optional)', null=True, upload_to=menus.models.menuitem_upload_to),
        ),
        migrations.AddField(
            model_name='menusection',
            name='image',
            field=models.ImageField(blank=True, help_text='An image or logo for this menu (optional)', null=True, upload_to=menus.models.menusection_upload_to),
        ),
        migrations.AlterField(
            model_name='menu',
            name='image',
            field=models.ImageField(blank=True, help_text='An image or logo for this menu (optional)', null=True, upload_to=menus.models.menu_upload_to),
        ),
    ]
