# Generated by Django 5.1.6 on 2025-03-09 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentApp', '0019_alter_car_condition'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenance',
            name='completed_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='priority',
            field=models.CharField(choices=[('normal', 'Обычный'), ('high', 'Высокий')], default='normal', max_length=20),
        ),
        migrations.AddField(
            model_name='maintenance',
            name='status',
            field=models.CharField(choices=[('pending', 'В ожидании'), ('in_progress', 'В работе'), ('completed', 'Завершено')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='maintenance',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='maintenance',
            name='description',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
