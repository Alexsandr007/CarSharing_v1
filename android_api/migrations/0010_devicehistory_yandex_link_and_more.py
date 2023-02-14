# Generated by Django 4.1.6 on 2023-02-09 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('android_api', '0009_remove_devicehistory_state_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicehistory',
            name='yandex_link',
            field=models.CharField(blank=True, max_length=625, null=True),
        ),
        migrations.AddField(
            model_name='historicaldevicehistory',
            name='yandex_link',
            field=models.CharField(blank=True, max_length=625, null=True),
        ),
        migrations.AlterField(
            model_name='devicehistory',
            name='all_activity_metrics',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='historicaldevicehistory',
            name='all_activity_metrics',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
