# Generated manually for adding created_at

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0005_alter_volunteerregistration_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteerregistration',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]