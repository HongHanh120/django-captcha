# Generated by Django 3.1.3 on 2021-04-24 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('captchaimages', '0005_auto_20210424_1712'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='remote_url',
        ),
        migrations.AddField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, upload_to='images/'),
        ),
    ]
