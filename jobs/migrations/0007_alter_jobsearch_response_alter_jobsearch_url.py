# Generated by Django 5.0.7 on 2024-07-19 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_jobsearch_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobsearch',
            name='response',
            field=models.CharField(blank=True, choices=[('lkpsearch', 'LKPSearch'), ('cislack', 'CISLACK'), ('lkjobsug', 'LKJOBSUG'), ('inform', 'INFORM')], default='lkpsearch', max_length=127, null=True),
        ),
        migrations.AlterField(
            model_name='jobsearch',
            name='url',
            field=models.URLField(blank=True, max_length=300, null=True),
        ),
    ]
