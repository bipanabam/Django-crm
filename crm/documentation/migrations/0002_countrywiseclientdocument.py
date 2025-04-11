# Generated by Django 5.1.7 on 2025-04-10 15:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0001_initial'),
        ('sales', '0002_client_branch'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryWiseClientDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_file', models.ImageField(upload_to='country/client_documents/')),
                ('uploaded_date', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='countrywisedocument', to='sales.client')),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='documentation.country')),
                ('document_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='documentation.documenttype')),
            ],
        ),
    ]
