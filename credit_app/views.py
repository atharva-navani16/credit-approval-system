from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import date, timedelta
from .models import Customer, Loan
from .serializers import *
from .utils import check_loan_eligibility, calculate_monthly_installment

@api_view(['POST'])
def register_customer(request):
    """Register a new customer"""
    serializer = CustomerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        response_serializer = CustomerRegistrationResponseSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def check_eligibility(request):
    """Check loan eligibility for a customer"""
    serializer = LoanEligibilitySerializer(data=request.data)
    if serializer.is_valid():
        eligibility_data = check_loan_eligibility(
            serializer.validated_data['customer_id'],
            serializer.validated_data['loan_amount'],
            serializer.validated_data['interest_rate'],
            serializer.validated_data['tenure']
        )
        response_serializer = LoanEligibilityResponseSerializer(eligibility_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_loan(request):
    """Create a new loan if eligible"""
    serializer = LoanCreationSerializer(data=request.data)
    if serializer.is_valid():
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']
        
        eligibility = check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure)
        
        if eligibility['approval']:
            try:
                customer = Customer.objects.get(customer_id=customer_id)
                
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    tenure=tenure,
                    interest_rate=eligibility['corrected_interest_rate'],
                    monthly_repayment=eligibility['monthly_installment'],
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=30*tenure)
                )
                
                customer.current_debt += loan_amount
                customer.save()
                
                response_data = {
                    'loan_id': loan.loan_id,
                    'customer_id': customer_id,
                    'loan_approved': True,
                    'message': 'Loan approved successfully',
                    'monthly_installment': eligibility['monthly_installment']
                }
                
            except Customer.DoesNotExist:
                response_data = {
                    'loan_id': None,
                    'customer_id': customer_id,
                    'loan_approved': False,
                    'message': 'Customer not found',
                    'monthly_installment': 0
                }
        else:
            response_data = {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': 'Loan not approved due to low credit score or high EMI ratio',
                'monthly_installment': eligibility['monthly_installment']
            }
        
        response_serializer = LoanCreationResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_loan(request, loan_id):
    """View loan details by loan ID"""
    try:
        loan = Loan.objects.select_related('customer').get(loan_id=loan_id)
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Loan not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """View all loans for a customer"""
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer)
        serializer = LoanListSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )