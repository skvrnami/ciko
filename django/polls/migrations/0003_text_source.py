# Generated by Django 5.1.3 on 2024-11-25 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_text_deleted_text_read_alter_text_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='text',
            name='source',
            field=models.CharField(default='', max_length=100),
        ),
    ]
