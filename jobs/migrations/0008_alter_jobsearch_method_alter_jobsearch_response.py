# Generated by Django 5.0.7 on 2024-07-19 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_alter_jobsearch_response_alter_jobsearch_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobsearch',
            name='method',
            field=models.CharField(blank=True, choices=[('lkpsearch', 'LKPSearch'), ('cislack', 'CISLACK'), ('lkjobsug', 'LKJOBSUG'), ('inform', 'INFORM')], default='lkpsearch', max_length=127, null=True),
        ),
        migrations.AlterField(
            model_name='jobsearch',
            name='response',
            field=models.CharField(blank=True, default=None, max_length=127, null=True),
        ),
    ]
