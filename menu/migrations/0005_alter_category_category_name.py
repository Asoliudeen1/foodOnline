# Generated by Django 4.1.1 on 2022-10-18 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_alter_category_updated_at_alter_fooditem_food_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category_name',
            field=models.CharField(max_length=50),
        ),
    ]