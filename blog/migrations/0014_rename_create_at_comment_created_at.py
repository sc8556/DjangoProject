# Generated by Django 5.2.1 on 2025-06-13 23:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0013_comment"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="create_at",
            new_name="created_at",
        ),
    ]
