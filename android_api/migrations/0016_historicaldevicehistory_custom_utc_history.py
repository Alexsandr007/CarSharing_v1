# Generated by Django 4.1.6 on 2023-02-14 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('android_api', '0015_devicehistory_custom_utc_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaldevicehistory',
            name='custom_utc_history',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
