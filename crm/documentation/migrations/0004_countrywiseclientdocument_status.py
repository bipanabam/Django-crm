# Generated by Django 5.1.7 on 2025-04-15 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0003_countrywiseclientdocument_uploaded_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='countrywiseclientdocument',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Approved', 'Approved')], default='Pending', max_length=15),
        ),
    ]
