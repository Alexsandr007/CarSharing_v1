# Generated by Django 4.1.6 on 2023-02-14 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('android_api', '0014_data_custom_utc'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicehistory',
            name='custom_utc',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaldevicehistory',
            name='custom_utc',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
    ]
