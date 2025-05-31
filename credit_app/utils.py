from decimal import Decimal
from datetime import datetime, date
from .models import Customer, Loan
import math

def calculate_credit_score(customer):
    """Calculate credit score based on historical loan data"""
    loans = Loan.objects.filter(customer=customer)
    
    if not loans.exists():
        return 50  # Default score for new customers
    
    # Component 1: Past Loans paid on time (40% weightage)
    total_emis = sum(loan.tenure for loan in loans)
    emis_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
    on_time_ratio = emis_paid_on_time / total_emis if total_emis > 0 else 0
    on_time_score = on_time_ratio * 40
    
    # Component 2: Number of loans taken (20% weightage)
    num_loans = loans.count()
    if num_loans <= 2:
        loan_count_score = 20
    elif num_loans <= 5:
        loan_count_score = 15
    elif num_loans <= 10:
        loan_count_score = 10
    else:
        loan_count_score = 5
    
    # Component 3: Loan activity in current year (20% weightage)
    current_year = datetime.now().year
    current_year_loans = loans.filter(start_date__year=current_year)
    if current_year_loans.count() <= 2:
        current_year_score = 20
    elif current_year_loans.count() <= 4:
        current_year_score = 15
    else:
        current_year_score = 10
    
    # Component 4: Loan approved volume (20% weightage)
    total_loan_amount = sum(loan.loan_amount for loan in loans)
    if total_loan_amount <= customer.approved_limit * Decimal('0.5'):
        volume_score = 20
    elif total_loan_amount <= customer.approved_limit:
        volume_score = 15
    else:
        volume_score = 5
    
    credit_score = on_time_score + loan_count_score + current_year_score + volume_score
    
    # Component 5: Check if sum of current loans > approved limit
    current_loans_sum = sum(loan.loan_amount for loan in loans if loan.end_date >= date.today())
    if current_loans_sum > customer.approved_limit:
        return 0
    
    return min(100, max(0, credit_score))

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    """Calculate monthly installment using compound interest formula"""
    monthly_rate = interest_rate / (12 * 100)
    if monthly_rate == 0:
        return loan_amount / tenure
    
    numerator = loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure)
    denominator = ((1 + monthly_rate) ** tenure) - 1
    return numerator / denominator

def get_corrected_interest_rate(credit_score, requested_rate):
    """Get corrected interest rate based on credit score"""
    if credit_score > 50:
        return requested_rate
    elif 30 < credit_score <= 50:
        return max(requested_rate, Decimal('12.0'))
    elif 10 < credit_score <= 30:
        return max(requested_rate, Decimal('16.0'))
    else:
        return requested_rate  # Won't be approved anyway

def check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure):
    """Check loan eligibility and return approval decision"""
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return {
            'customer_id': customer_id,
            'approval': False,
            'interest_rate': interest_rate,
            'corrected_interest_rate': interest_rate,
            'tenure': tenure,
            'monthly_installment': Decimal('0')
        }
    
    credit_score = calculate_credit_score(customer)
    corrected_rate = get_corrected_interest_rate(credit_score, interest_rate)
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_rate, tenure)
    
    current_loans = Loan.objects.filter(
        customer=customer,
        end_date__gte=date.today()
    )
    current_emis = sum(loan.monthly_repayment for loan in current_loans)
    total_emis_after_loan = current_emis + monthly_installment
    
    approval = True
    
    if credit_score <= 10:
        approval = False
    elif 10 < credit_score <= 30 and corrected_rate < 16:
        approval = False
    elif 30 < credit_score <= 50 and corrected_rate < 12:
        approval = False
    
    if total_emis_after_loan > customer.monthly_salary * Decimal('0.5'):
        approval = False
    
    return {
        'customer_id': customer_id,
        'approval': approval,
        'interest_rate': interest_rate,
        'corrected_interest_rate': corrected_rate,
        'tenure': tenure,
        'monthly_installment': monthly_installment
    }