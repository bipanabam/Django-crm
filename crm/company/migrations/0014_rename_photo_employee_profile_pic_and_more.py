# Generated by Django 5.1.7 on 2025-05-16 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0013_remove_employee_role_employee_blood_type_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='photo',
            new_name='profile_pic',
        ),
        migrations.AlterField(
            model_name='employee',
            name='emergency_contact_relationship',
            field=models.CharField(blank=True, choices=[('Father', 'Father'), ('Mother', 'Mother'), ('Spouse', 'Spouse'), ('Son', 'Son'), ('Daughter', 'Daughter'), ('Brother', 'Brother'), ('Sister', 'Sister'), ('Other', 'Other')], max_length=50, null=True),
        ),
    ]
