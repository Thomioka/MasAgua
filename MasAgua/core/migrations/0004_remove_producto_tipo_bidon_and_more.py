# Generated by Django 5.0.6 on 2025-06-27 00:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_plan_producto_cliente_contrato'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producto',
            name='tipo_bidon',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='tipo_dispensador',
        ),
    ]
