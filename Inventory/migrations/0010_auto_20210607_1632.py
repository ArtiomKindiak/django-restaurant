# Generated by Django 2.2 on 2021-06-07 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inventory', '0009_ingredient_update_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='update_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=models.DecimalField(decimal_places=2, max_digits=6), max_digits=6, null=True),
        ),
    ]