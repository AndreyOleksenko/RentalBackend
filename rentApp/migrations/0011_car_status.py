# Generated by Django 5.1.6 on 2025-03-05 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentApp', '0010_rental_rejection_reason_alter_rental_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='status',
            field=models.CharField(choices=[('available', 'Доступна'), ('in_rent', 'В аренде'), ('maintenance', 'На обслуживании'), ('pending', 'Ожидает подтверждения')], default='available', max_length=20),
        ),
    ]
