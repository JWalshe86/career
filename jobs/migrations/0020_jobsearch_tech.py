# Generated by Django 5.0.7 on 2024-08-02 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0019_alter_jobsearch_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobsearch',
            name='tech',
            field=models.CharField(blank=True, max_length=127, null=True),
        ),
    ]
