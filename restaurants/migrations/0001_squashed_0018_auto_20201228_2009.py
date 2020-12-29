# Generated by Django 3.1.4 on 2020-12-29 03:17

from django.conf import settings
from django.db import migrations, models
import restaurants.models


class Migration(migrations.Migration):

    replaces = [('restaurants', '0001_initial'), ('restaurants', '0002_auto_20201020_2046'), ('restaurants', '0003_auto_20201020_2049'), ('restaurants', '0004_auto_20201020_2054'), ('restaurants', '0005_auto_20201020_2055'), ('restaurants', '0006_auto_20201020_2055'), ('restaurants', '0007_auto_20201020_2056'), ('restaurants', '0008_auto_20201020_2057'), ('restaurants', '0009_auto_20201020_2058'), ('restaurants', '0010_auto_20201020_2058'), ('restaurants', '0011_auto_20201022_0436'), ('restaurants', '0012_auto_20201022_0438'), ('restaurants', '0013_auto_20201025_0052'), ('restaurants', '0014_auto_20201025_2114'), ('restaurants', '0015_auto_20201228_0956'), ('restaurants', '0016_auto_20201228_1002'), ('restaurants', '0017_auto_20201228_1003'), ('restaurants', '0018_auto_20201228_2009')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=128)),
                ('slug', models.SlugField(default=None, max_length=128, unique=True)),
                ('admin_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('image', models.ImageField(blank=True, help_text='An image or logo for your restaurant (optional)', null=True, upload_to=restaurants.models.upload_to)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
