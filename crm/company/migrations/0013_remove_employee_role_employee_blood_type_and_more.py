# Generated by Django 5.1.7 on 2025-05-16 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0012_user_last_seen_user_online_status_delete_userstatus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='role',
        ),
        migrations.AddField(
            model_name='employee',
            name='blood_type',
            field=models.CharField(choices=[('A+', 'A+'), ('B+', 'B+'), ('AB+', 'AB+'), ('O+', 'O+'), ('A-', 'A-'), ('B-', 'B-'), ('AB-', 'AB-'), ('O-', 'O-')], default='A+', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='citizenship_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='current_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='emergency_contact_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='emergency_contact_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='emergency_contact_number',
            field=models.CharField(blank=True, max_length=14, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='emergency_contact_relationship',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Father', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='marital_status',
            field=models.CharField(blank=True, choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=14, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='pan_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='permanent_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='employee_photos/'),
        ),
        migrations.AddField(
            model_name='employee',
            name='signature',
            field=models.ImageField(blank=True, null=True, upload_to='employee_signatures/'),
        ),
    ]
