# Generated by Django 5.0.7 on 2024-07-23 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0010_jobsearch_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobsearch',
            name='method',
            field=models.CharField(blank=True, choices=[('lkpsearch', 'LKPSearch'), ('cislack', 'CISLACK'), ('lkjobsug', 'LKJOBSUG'), ('inform', 'INFORM'), ('irishjobs.ie', 'IRISHJOBS.IE')], default='lkpsearch', max_length=127, null=True),
        ),
    ]
