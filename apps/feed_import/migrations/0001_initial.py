# Generated by Django 2.0 on 2020-06-16 06:52

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OAuthToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(blank=True, max_length=50, null=True)),
                ('uuid', models.CharField(blank=True, max_length=50, null=True)),
                ('remote_ip', models.CharField(blank=True, max_length=50, null=True)),
                ('request_token', models.CharField(max_length=50)),
                ('request_token_secret', models.CharField(max_length=50)),
                ('access_token', models.CharField(max_length=50)),
                ('access_token_secret', models.CharField(max_length=50)),
                ('credential', models.TextField(blank=True, null=True)),
                ('created_date', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
