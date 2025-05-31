from django.core.management.base import BaseCommand
from credit_app.tasks import ingest_customer_data, ingest_loan_data

class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['customers', 'loans', 'all'],
            default='all',
            help='Type of data to ingest'
        )

    def handle(self, *args, **options):
        data_type = options['type']
        
        if data_type in ['customers', 'all']:
            self.stdout.write('Ingesting customer data...')
            result = ingest_customer_data()
            self.stdout.write(self.style.SUCCESS(result))
        
        if data_type in ['loans', 'all']:
            self.stdout.write('Ingesting loan data...')
            result = ingest_loan_data()
            self.stdout.write(self.style.SUCCESS(result))