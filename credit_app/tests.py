from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Customer, Loan
from .utils import calculate_credit_score, calculate_monthly_installment

class CustomerModelTest(TestCase):
    def test_customer_creation(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number=9876543210,
            monthly_salary=50000,
            approved_limit=1800000
        )
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.approved_limit, 1800000)

class CreditScoreTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            phone_number=9876543210,
            monthly_salary=50000,
            approved_limit=1800000
        )

    def test_credit_score_new_customer(self):
        score = calculate_credit_score(self.customer)
        self.assertEqual(score, 50)

class APITestCase(APITestCase):
    def test_register_customer(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "monthly_income": 50000,
            "phone_number": 9876543210
        }
        response = self.client.post('/api/register', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(response.data['approved_limit']), 1800000.0)

    def test_check_eligibility(self):
        customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            phone_number=9876543210,
            monthly_salary=50000,
            approved_limit=1800000
        )
        
        data = {
            "customer_id": customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 10.0,
            "tenure": 12
        }
        response = self.client.post('/api/check-eligibility', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)