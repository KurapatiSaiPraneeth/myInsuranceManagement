# Generated by Django 4.2 on 2023-04-11 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0005_policyrecord_auto_renew_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policyrecord',
            name='auto_renew',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
