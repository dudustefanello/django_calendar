# Generated by Django 5.1.1 on 2024-09-19 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='color',
            field=models.CharField(blank=True, choices=[('primary', 'primary'), ('success', 'success'), ('warning', 'warning'), ('danger', 'danger'), ('info', 'info')], max_length=16, null=True),
        ),
    ]
