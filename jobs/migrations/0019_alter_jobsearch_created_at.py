# Generated by Django 5.0.7 on 2024-08-02 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0018_alter_jobsearch_options_alter_jobsearch_response'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobsearch',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]
