# Generated by Django 4.1.1 on 2022-10-19 18:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0004_openinghour'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='openinghour',
            options={'ordering': ('day', '-from_hour')},
        ),
        migrations.AlterUniqueTogether(
            name='openinghour',
            unique_together={('vendor', 'day', 'from_hour', 'to_hour')},
        ),
    ]
