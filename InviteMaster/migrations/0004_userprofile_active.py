# Generated by Django 4.2.11 on 2024-04-21 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InviteMaster', '0003_remove_userprofile_already_used_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]