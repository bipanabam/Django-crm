# Generated by Django 5.1.7 on 2025-04-19 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0005_employee_access_level_employee_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('manager', 'Manager'), ('accountant', 'Accountant'), ('sales representative', 'Sales Representative')], default='accountant', max_length=20),
        ),
    ]
