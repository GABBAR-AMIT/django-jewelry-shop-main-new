# Generated by Django 4.2.2 on 2023-11-17 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webb', '0002_alter_color_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcolor',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is Active?'),
        ),
    ]
