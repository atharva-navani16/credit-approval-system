from django.core.management.base import BaseCommand
from credit_app.models import Customer
from credit_app.utils import calculate_credit_score

class Command(BaseCommand):
    help = 'Calculate and display credit scores for all customers'

    def handle(self, *args, **options):
        customers = Customer.objects.all()
        
        for customer in customers:
            score = calculate_credit_score(customer)
            self.stdout.write(
                f"Customer {customer.customer_id} ({customer.name}): Credit Score = {score}"
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Calculated scores for {customers.count()} customers')
        )