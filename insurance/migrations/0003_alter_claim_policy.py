# Generated by Django 3.2.13 on 2023-03-23 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0002_claim'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='policy',
            field=models.CharField(max_length=200),
        ),
    ]
