import csv
from django.core.management.base import BaseCommand
from datetime import date
from itertools import islice
from django.conf import settings
from jobs.models import Lkdata


class Command(BaseCommand):
    help = 'Load data from Linkedin Analytics file'

    def handle(self, *args, **kwargs):
        datafile = settings.BASE_DIR / 'data' / 'lk_mets.csv'

        with open(datafile, 'r') as csvfile:
            reader = csv.DictReader(islice(csvfile, None))

            for row in reader:
                dt = date(
                year = int(row['year']),
                month = int(row['month']),
                day = int(row['day']), 
                )
                Lkdata.objects.get_or_create(date=dt, impressions=row['impressions'],
                srch_appears=row['srch_appears'],uni_views=row['uni_views'], engagements=row['engagements'], followers=row['followers'])



