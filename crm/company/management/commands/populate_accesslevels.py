from django.core.management.base import BaseCommand
from company.models import AccessLevel

class Command(BaseCommand):
    help = 'Populates AccessLevel table with initial data.'

    def handle(self, *args, **options):
        access_levels = [
            'Admin',
            'Manager',
            'Team Manager',
            'Accountant',
            'Sales Representative',
            'Counsellor',
            'Marketing'
        ]

        for level in access_levels:
            obj, created = AccessLevel.objects.get_or_create(name=level)
            if created:
                self.stdout.write(self.style.SUCCESS(f'AccessLevel "{level}" created.'))
            else:
                self.stdout.write(f'AccessLevel "{level}" already exists.')

